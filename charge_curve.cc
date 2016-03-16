/* Copyright (c) 2016, the Cap authors.
 *
 * This file is subject to the Modified BSD License and may not be distributed
 * without copyright and license information. Please refer to the file LICENSE
 * for the text and further information on this license. 
 */

#include <cap/energy_storage_device.h>
#include <cap/utils.h>
#include <boost/format.hpp>
#include <boost/foreach.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/xml_parser.hpp>
#include <iostream>
#include <fstream>
#include <iterator>
#include <algorithm>

namespace cap {

std::function<void(double const, double const, std::shared_ptr<cap::EnergyStorageDevice>)>
get_charge_evolve_one_time_step(std::string const & charge_mode, std::shared_ptr<boost::property_tree::ptree const> database)
{
    if (charge_mode.compare("constant_current") == 0) {
        double const charge_current = database->get<double>("charge_current");
        return [charge_current](double const, double const time_step, std::shared_ptr<cap::EnergyStorageDevice> dev)
            { dev->evolve_one_time_step_constant_current(time_step, charge_current); };
    } else if (charge_mode.compare("constant_power") == 0) {
        double const charge_power = database->get<double>("charge_power");
        return [charge_power](double const, double const time_step, std::shared_ptr<cap::EnergyStorageDevice> dev)
            { dev->evolve_one_time_step_constant_power(time_step, charge_power); };
    } else {
        throw std::runtime_error("invalid charge mode "+charge_mode);
    }
}



std::function<bool(double const, std::shared_ptr<cap::EnergyStorageDevice>)>
get_charge_end_criterion(std::string const & charge_stop_at, double const tick, std::shared_ptr<boost::property_tree::ptree const> database)
{
    if (charge_stop_at.compare("voltage_greater_than") == 0) {
        double const charge_voltage_limit = database->get<double>("charge_voltage_limit");
        return [charge_voltage_limit](double const, std::shared_ptr<cap::EnergyStorageDevice> dev)
            { double voltage; dev->get_voltage(voltage); return (voltage >= charge_voltage_limit); };
    } else if (charge_stop_at.compare("time_greater_than") == 0) {
        double const charge_duration = database->get<double>("charge_duration");
        return [charge_duration, tick](double const time, std::shared_ptr<cap::EnergyStorageDevice>)
            { return (time - tick >= charge_duration); };
    } else {
        throw std::runtime_error("invalid test stop at "+charge_stop_at);
    }
}



void charge_curve(std::shared_ptr<cap::EnergyStorageDevice> dev, std::shared_ptr<boost::property_tree::ptree const> database, std::ostream & os = std::cout)
{
    double time = 0.0;
    std::string const charge_mode    = database->get<std::string>("charge_mode"   );
    auto evolve_one_time_step = get_charge_evolve_one_time_step(charge_mode, database);
    std::string const charge_stop_at = database->get<std::string>("charge_stop_at");
    auto end_criterion = get_charge_end_criterion(charge_stop_at, time, database);

    double const max_charge_time = database->get<double>("max_charge_time");
    double const time_step       = database->get<double>("time_step"         );
    double const initial_voltage = database->get<double>("initial_voltage"   );
    dev->reset_voltage(initial_voltage);

    double tick = time;
    while (time - tick < max_charge_time)
    {
        evolve_one_time_step(time, time_step, dev);
        time += time_step;
        if (end_criterion(time, dev))
            break;
    }

    // optional charge votage finish (default value is false)
    bool const charge_voltage_finish = database->get<bool>("charge_voltage_finish", false);
    if (charge_voltage_finish) {
        double const charge_voltage_finish_max_time      = database->get<double>("charge_voltage_finish_max_time"     );
        double const charge_voltage_finish_current_limit = database->get<double>("charge_voltage_finish_current_limit");
        double       current;
        double const constant_voltage = database->get<double>("charge_voltage_limit");
        tick = time;
        while (time < max_charge_time)
        {
            dev->evolve_one_time_step_constant_voltage(time_step, constant_voltage);
            time += time_step;
            dev->get_current(current);
            if ((time - tick >= charge_voltage_finish_max_time)
                || (current <= charge_voltage_finish_current_limit))
                break;
        }
    } // end charge voltage finish
}

} // end namespace cap



int main()
{
    // parse input file
    std::shared_ptr<boost::property_tree::ptree> input_database =
        std::make_shared<boost::property_tree::ptree>();
    boost::property_tree::xml_parser::read_xml("input_charge_curve", *input_database,
        boost::property_tree::xml_parser::trim_whitespace | boost::property_tree::xml_parser::no_comments);

    // build an energy storage system
    auto device_database = input_database->get_child("device");
    std::shared_ptr<cap::EnergyStorageDevice> device =
        cap::buildEnergyStorageDevice(boost::mpi::communicator(), device_database);

    // measure charge curve
    std::shared_ptr<boost::property_tree::ptree> charge_curve_database =
        std::make_shared<boost::property_tree::ptree>(input_database->get_child("charge_curve"));
    cap::charge_curve(device, charge_curve_database);

    return 0;
}    
