/* Copyright (c) 2016, the Cap authors.
 *
 * This file is subject to the Modified BSD License and may not be distributed
 * without copyright and license information. Please refer to the file LICENSE
 * for the text and further information on this license. 
 */

#include <cap/resistor_capacitor.h>
#include <boost/format.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/info_parser.hpp>
#include <boost/test/floating_point_comparison.hpp>
#include <cmath>
#include <iostream>
#include <fstream>



namespace cap {

void measure_direct_leakage_current(std::shared_ptr<cap::EnergyStorageDevice> dev, std::shared_ptr<boost::property_tree::ptree const> database)
{
    double const dc_voltage          = database->get<double>("dc_voltage"         );
    double const initial_voltage     = database->get<double>("initial_voltage"    );
    double const initial_time        = database->get<double>("initial_time"       );
    double const final_time          = database->get<double>("final_time"         );
    double const time_step           = database->get<double>("time_step"          );
    double const percent_tolerance   = database->get<double>("percent_tolerance"  );

    double voltage;
    double current;
    double current_previous_time_step = std::numeric_limits<double>::quiet_NaN();
    dev->reset_voltage(initial_voltage);
    std::size_t step = 0;
    for (double time = initial_time; time < final_time; time += time_step)
    {
        ++step;
        dev->get_current(current);
        dev->get_voltage(voltage);
        dev->evolve_one_time_step_constant_voltage(time_step, dc_voltage);
        if (std::abs(current - current_previous_time_step) / std::abs(current) < percent_tolerance)
            break;
        current_previous_time_step = current;
    }
}



void measure_self_discharge(std::shared_ptr<cap::EnergyStorageDevice> dev, std::shared_ptr<boost::property_tree::ptree const> database)
{
    double const initial_time        = database->get<double>("initial_time"       );
    double const final_time          = database->get<double>("final_time"         );
    double const time_step           = database->get<double>("time_step"          );

    double voltage;
    double current;
    std::size_t step = 0;
    for (double time = initial_time; time < final_time; time += time_step)
    {
        ++step;
        dev->get_current(current);
        dev->get_voltage(voltage);
        dev->evolve_one_time_step_constant_current(time_step, 0.0);
    }
}

} // end namespace cap

int main()
{
    // parse input file
    std::shared_ptr<boost::property_tree::ptree> input_database =
        std::make_shared<boost::property_tree::ptree>();
    boost::property_tree::info_parser::read_info("input_leakage_current.info", *input_database);

    // build an energy storage system
    std::shared_ptr<boost::property_tree::ptree> device_database =
        std::make_shared<boost::property_tree::ptree>(input_database->get_child("device"));
    std::shared_ptr<cap::EnergyStorageDevice> device =
        cap::buildEnergyStorageDevice(boost::mpi::communicator(), *device_database);

    // apply a DC voltage to and measure the current required to maintain that voltage
    std::shared_ptr<boost::property_tree::ptree> direct_leakage_database =
        std::make_shared<boost::property_tree::ptree>(input_database->get_child("direct_leakage"));
    cap::measure_direct_leakage_current(device, direct_leakage_database);

    // device is charged.  now measure the change of the open circuit potential
    std::shared_ptr<boost::property_tree::ptree> sef_discharge_database =
        std::make_shared<boost::property_tree::ptree>(input_database->get_child("self_discharge"));
    cap::measure_self_discharge(device, sef_discharge_database);

}    
