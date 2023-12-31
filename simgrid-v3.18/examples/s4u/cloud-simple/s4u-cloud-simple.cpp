/* Copyright (c) 2007-2017. The SimGrid Team. All rights reserved.          */

/* This program is free software; you can redistribute it and/or modify it
 * under the terms of the license (GNU LGPL) which comes with this package. */

#include "simgrid/s4u.hpp"
#include "simgrid/s4u/VirtualMachine.hpp"
XBT_LOG_NEW_DEFAULT_CATEGORY(s4u_test, "Messages specific for this s4u example");

static void computation_fun()
{
  double clock_sta = simgrid::s4u::Engine::getClock();
  simgrid::s4u::this_actor::execute(1000000);
  double clock_end = simgrid::s4u::Engine::getClock();

  XBT_INFO("%s:%s task executed %g", simgrid::s4u::this_actor::getHost()->getCname(),
           simgrid::s4u::this_actor::getCname(), clock_end - clock_sta);
}

static void launch_computation_worker(s4u_Host* host)
{
  simgrid::s4u::Actor::createActor("compute", host, computation_fun);
}

struct s_payload {
  s4u_Host* tx_host;
  const char* tx_actor_name;
  double clock_sta;
};

static void communication_tx_fun(std::vector<std::string> args)
{
  simgrid::s4u::MailboxPtr mbox = simgrid::s4u::Mailbox::byName(args.at(0));
  struct s_payload* payload     = xbt_new(struct s_payload, 1);
  payload->tx_actor_name        = simgrid::s4u::Actor::self()->getCname();
  payload->tx_host              = simgrid::s4u::this_actor::getHost();
  payload->clock_sta            = simgrid::s4u::Engine::getClock();

  mbox->put(payload, 1000000);
}

static void communication_rx_fun(std::vector<std::string> args)
{
  const char* actor_name        = simgrid::s4u::Actor::self()->getCname();
  const char* host_name         = simgrid::s4u::this_actor::getHost()->getCname();
  simgrid::s4u::MailboxPtr mbox = simgrid::s4u::Mailbox::byName(args.at(0));

  struct s_payload* payload = static_cast<struct s_payload*>(mbox->get());
  double clock_end          = simgrid::s4u::Engine::getClock();

  XBT_INFO("%s:%s to %s:%s => %g sec", payload->tx_host->getCname(), payload->tx_actor_name, host_name, actor_name,
           clock_end - payload->clock_sta);

  xbt_free(payload);
}

static void launch_communication_worker(s4u_Host* tx_host, s4u_Host* rx_host)
{
  std::string mbox_name = std::string("MBOX:") + tx_host->getCname() + "-" + rx_host->getCname();
  std::vector<std::string> args;
  args.push_back(mbox_name);

  simgrid::s4u::Actor::createActor("comm_tx", tx_host, communication_tx_fun, args);

  simgrid::s4u::Actor::createActor("comm_rx", rx_host, communication_rx_fun, args);
}

static void master_main()
{
  s4u_Host* pm0 = simgrid::s4u::Host::by_name("Fafard");
  s4u_Host* pm1 = simgrid::s4u::Host::by_name("Tremblay");

  XBT_INFO("## Test 1 (started): check computation on normal PMs");

  XBT_INFO("### Put a task on a PM");
  launch_computation_worker(pm0);
  simgrid::s4u::this_actor::sleep_for(2);

  XBT_INFO("### Put two tasks on a PM");
  launch_computation_worker(pm0);
  launch_computation_worker(pm0);
  simgrid::s4u::this_actor::sleep_for(2);

  XBT_INFO("### Put a task on each PM");
  launch_computation_worker(pm0);
  launch_computation_worker(pm1);
  simgrid::s4u::this_actor::sleep_for(2);

  XBT_INFO("## Test 1 (ended)");

  XBT_INFO("## Test 2 (started): check impact of running a task inside a VM (there is no degradation for the moment)");

  XBT_INFO("### Put a VM on a PM, and put a task to the VM");
  simgrid::s4u::VirtualMachine* vm0 = new simgrid::s4u::VirtualMachine("VM0", pm0, 1);
  vm0->start();
  launch_computation_worker(vm0);
  simgrid::s4u::this_actor::sleep_for(2);
  vm0->destroy();

  XBT_INFO("## Test 2 (ended)");

  XBT_INFO(
      "## Test 3 (started): check impact of running a task collocated with a VM (there is no VM noise for the moment)");

  XBT_INFO("### Put a VM on a PM, and put a task to the PM");
  vm0 = new simgrid::s4u::VirtualMachine("VM0", pm0, 1);
  vm0->start();
  launch_computation_worker(pm0);
  simgrid::s4u::this_actor::sleep_for(2);
  vm0->destroy();
  XBT_INFO("## Test 3 (ended)");

  XBT_INFO("## Test 4 (started): compare the cost of running two tasks inside two different VMs collocated or not (for"
           " the moment, there is no degradation for the VMs. Hence, the time should be equals to the time of test 1");

  XBT_INFO("### Put two VMs on a PM, and put a task to each VM");
  vm0 = new simgrid::s4u::VirtualMachine("VM0", pm0, 1);
  vm0->start();
  simgrid::s4u::VirtualMachine* vm1 = new simgrid::s4u::VirtualMachine("VM1", pm0, 1);
  launch_computation_worker(vm0);
  launch_computation_worker(vm1);
  simgrid::s4u::this_actor::sleep_for(2);
  vm0->destroy();
  vm1->destroy();

  XBT_INFO("### Put a VM on each PM, and put a task to each VM");
  vm0 = new simgrid::s4u::VirtualMachine("VM0", pm0, 1);
  vm1 = new simgrid::s4u::VirtualMachine("VM1", pm1, 1);
  vm0->start();
  vm1->start();
  launch_computation_worker(vm0);
  launch_computation_worker(vm1);
  simgrid::s4u::this_actor::sleep_for(2);
  vm0->destroy();
  vm1->destroy();
  XBT_INFO("## Test 4 (ended)");

  XBT_INFO("## Test 5  (started): Analyse network impact");
  XBT_INFO("### Make a connection between PM0 and PM1");
  launch_communication_worker(pm0, pm1);
  simgrid::s4u::this_actor::sleep_for(5);

  XBT_INFO("### Make two connection between PM0 and PM1");
  launch_communication_worker(pm0, pm1);
  launch_communication_worker(pm0, pm1);
  simgrid::s4u::this_actor::sleep_for(5);

  XBT_INFO("### Make a connection between PM0 and VM0@PM0");
  vm0 = new simgrid::s4u::VirtualMachine("VM0", pm0, 1);
  vm0->start();
  launch_communication_worker(pm0, vm0);
  simgrid::s4u::this_actor::sleep_for(5);
  vm0->destroy();

  XBT_INFO("### Make a connection between PM0 and VM0@PM1");
  vm0 = new simgrid::s4u::VirtualMachine("VM0", pm1, 1);
  launch_communication_worker(pm0, vm0);
  simgrid::s4u::this_actor::sleep_for(5);
  vm0->destroy();

  XBT_INFO("### Make two connections between PM0 and VM0@PM1");
  vm0 = new simgrid::s4u::VirtualMachine("VM0", pm1, 1);
  vm0->start();
  launch_communication_worker(pm0, vm0);
  launch_communication_worker(pm0, vm0);
  simgrid::s4u::this_actor::sleep_for(5);
  vm0->destroy();

  XBT_INFO("### Make a connection between PM0 and VM0@PM1, and also make a connection between PM0 and PM1");
  vm0 = new simgrid::s4u::VirtualMachine("VM0", pm1, 1);
  vm0->start();
  launch_communication_worker(pm0, vm0);
  launch_communication_worker(pm0, pm1);
  simgrid::s4u::this_actor::sleep_for(5);
  vm0->destroy();

  XBT_INFO("### Make a connection between VM0@PM0 and PM1@PM1, and also make a connection between VM0@PM0 and VM1@PM1");
  vm0 = new simgrid::s4u::VirtualMachine("VM0", pm0, 1);
  vm1 = new simgrid::s4u::VirtualMachine("VM1", pm1, 1);
  vm0->start();
  vm1->start();
  launch_communication_worker(vm0, vm1);
  launch_communication_worker(vm0, vm1);
  simgrid::s4u::this_actor::sleep_for(5);
  vm0->destroy();
  vm1->destroy();

  XBT_INFO("## Test 5 (ended)");
}

int main(int argc, char* argv[])
{
  simgrid::s4u::Engine e(&argc, argv);
  e.loadPlatform(argv[1]); /* - Load the platform description */

  simgrid::s4u::Actor::createActor("master_", simgrid::s4u::Host::by_name("Fafard"), master_main);

  e.run();

  XBT_INFO("Simulation time %g", e.getClock());

  return 0;
}
