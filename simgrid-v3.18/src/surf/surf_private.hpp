/* Copyright (c) 2004-2017. The SimGrid Team. All rights reserved.          */

/* This program is free software; you can redistribute it and/or modify it
 * under the terms of the license (GNU LGPL) which comes with this package. */

#ifndef SURF_SURF_PRIVATE_HPP
#define SURF_SURF_PRIVATE_HPP

#include "src/surf/trace_mgr.hpp"
#include "surf/surf.hpp"

#define NO_MAX_DURATION -1.0

extern "C" {

extern XBT_PRIVATE const char* surf_action_state_names[6];

/** @ingroup SURF_interface
 * @brief Possible update mechanisms
 */
enum e_UM_t {
  UM_FULL,     /**< Full update mechanism: the remaining time of every action is recomputed at each step */
  UM_LAZY,     /**< Lazy update mechanism: only the modified actions get recomputed.
                    It may be slower than full if your system is tightly coupled to the point where every action
                    gets recomputed anyway. In that case, you'd better not try to be cleaver with lazy and go for
                    a simple full update.  */
  UM_UNDEFINED /**< Mechanism not defined */
};

/* Generic functions common to all models */

XBT_PRIVATE FILE* surf_fopen(const char* name, const char* mode);
XBT_PRIVATE std::ifstream* surf_ifsopen(std::string name);

/* The __surf_is_absolute_file_path() returns 1 if
 * file_path is a absolute file path, in the other
 * case the function returns 0.
 */
XBT_PRIVATE int __surf_is_absolute_file_path(const char* file_path);

extern XBT_PRIVATE simgrid::trace_mgr::future_evt_set* future_evt_set;

XBT_PUBLIC(void) storage_register_callbacks();

XBT_PRIVATE void parse_after_config();

/********** Tracing **********/
/* from surf_instr.c */
void TRACE_surf_host_set_speed(double date, const char* resource, double power);
void TRACE_surf_link_set_bandwidth(double date, const char* resource, double bandwidth);
}

#endif
