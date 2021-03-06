/* Copyright (c) 2016, the Cap authors.
 *
 * This file is subject to the Modified BSD License and may not be distributed
 * without copyright and license information. Please refer to the file LICENSE
 * for the text and further information on this license. 
 */

#include <cap/resistor_capacitor.h>
#include <boost/format.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/xml_parser.hpp>
#include <iostream>
#include <fstream>



namespace cap {

void scan(std::shared_ptr<cap::EnergyStorageDevice> dev, std::shared_ptr<boost::property_tree::ptree const> database)
{
    double const scan_rate           = database->get<double>("scan_rate"          );
    double const step_size           = database->get<double>("step_size"          );
    double const initial_voltage     = database->get<double>("initial_voltage"    );
    double const voltage_upper_limit = database->get<double>("voltage_upper_limit");
    double const voltage_lower_limit = database->get<double>("voltage_lower_limit");
    double const final_voltage       = database->get<double>("final_voltage"      );
    int    const cycles              = database->get<int   >("cycles"             );

    double const time_step = step_size / scan_rate;
    double time = 0.0;
    dev->reset_voltage(initial_voltage);
    double voltage = initial_voltage;
    for (int n = 0; n < cycles; ++n)
    {
        for ( ; voltage <= voltage_upper_limit; voltage += step_size, time+=time_step)
            dev->evolve_one_time_step_linear_voltage(time_step, voltage);
        
        for ( ; voltage >= voltage_lower_limit; voltage -= step_size, time+=time_step)
            dev->evolve_one_time_step_linear_voltage(time_step, voltage);
        
        for ( ; voltage <= final_voltage; voltage += step_size, time+=time_step)
            dev->evolve_one_time_step_linear_voltage(time_step, voltage);
        
    }
}

} // end namespace cap



int main()
{
    // parse input file
    std::shared_ptr<boost::property_tree::ptree> input_database =
        std::make_shared<boost::property_tree::ptree>();
    boost::property_tree::xml_parser::read_xml("input_cyclic_voltammetry", *input_database,
        boost::property_tree::xml_parser::trim_whitespace | boost::property_tree::xml_parser::no_comments);

    // build an energy storage system
    auto device_database = input_database->get_child("device");
    std::shared_ptr<cap::EnergyStorageDevice> device =
        cap::buildEnergyStorageDevice(boost::mpi::communicator(), device_database);

    // scan the system
    std::shared_ptr<boost::property_tree::ptree> cyclic_voltammetry_database =
        std::make_shared<boost::property_tree::ptree>(input_database->get_child("cyclic_voltammetry"));
    cap::scan(device, cyclic_voltammetry_database);

    return 0;
}    
