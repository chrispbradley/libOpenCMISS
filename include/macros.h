/* \file
 * \brief This file contains all pre-processing macros.
 *
 * \section LICENSE
 *
 * Version: MPL 1.1/GPL 2.0/LGPL 2.1
 *
 * The contents of this file are subject to the Mozilla Public License
 * Version 1.1 (the "License"); you may not use this file except in
 * compliance with the License. You may obtain a copy of the License at
 * http://www.mozilla.org/MPL/
 *
 * Software distributed under the License is distributed on an "AS IS"
 * basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
 * License for the specific language governing rights and limitations
 * under the License.
 *
 * The Original Code is OpenCMISS
 *
 * The Initial Developer of the Original Code is University of Auckland,
 * Auckland, New Zealand, the University of Oxford, Oxford, United
 * Kingdom and King's College, London, United Kingdom. Portions created
 * by the University of Auckland, the University of Oxford and King's
 * College, London are Copyright (C) 2007-2010 by the University of
 * Auckland, the University of Oxford and King's College, London.
 * All Rights Reserved.
 *
 * Contributor(s): Chris Bradley
 *
 * Alternatively, the contents of this file may be used under the terms of
 * either the GNU General Public License Version 2 or later (the "GPL"), or
 * the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
 * in which case the provisions of the GPL or the LGPL are applicable instead
 * of those above. If you wish to allow use of your version of this file only
 * under the terms of either the GPL or the LGPL, and not to allow others to
 * use your version of this file under the terms of the MPL, indicate your
 * decision by deleting the provisions above and replace them with the notice
 * and other provisions required by the GPL or the LGPL. If you do not delete
 * the provisions above, a recipient may use your version of this file under
 * the terms of any one of the MPL, the GPL or the LGPL.
 *
 */

#ifdef WITH_DIAGNOSTICS
#  define ENTERS(routinename,err,error,linenum) \
          CALL Enters(routinename,err,error,linenum)
#  define EXITS(routinename) \
	  CALL Exits(routinename)
#  define ERRORS(routinename,err,error) \
	  CALL Errors(routinename,err,error)
#  define ERRORSEXITS(routinename,err,error) \
	  CALL Errors(routinename,err,error); CALL Exits(routinename)
#else
#  define ENTERS(routinename,err,error,linenum) !Do nothing
#  define EXITS(routinename) !Do nothing
#  define ERRORS(routinename,err,error) \
	  CALL Errors(routinename,err,error)
#  define ERRORSEXITS(routinename,err,error) \
	  CALL Errors(routinename,err,error)
#endif

#ifdef WITH_NO_CHECKS
#  define WITH_NO_PRECHECKS
#  define WITH_NO_POSTCHECKS
#endif  
  
#ifndef WITH_NO_PRECHECKS
#  define WITH_PRECHECKS
#endif

#ifndef WITH_NO_POSTCHECKS
#  define WITH_POSTCHECKS
#endif

#if defined WITH_PRECHECKS || defined WITH_POSTCHECKS
#  define WITH_CHECKS
#endif

#ifdef WITH_MPI
#  define ASSERT_WITH_MPI() !Do nothing
#else
#  define ASSERT_WITH_MPI() \
   CALL FlagError("Must compile with WITH_MPI ON to use MPI functionality.",err,error,*999)
#endif

#ifdef WITH_CELLML
#  define ASSERT_WITH_CELLML() !Do nothing
#else
#  define ASSERT_WITH_CELLML() \
   CALL FlagError("Must compile with WITH_CELLML ON to use CellML functionality.",err,error,*999)
#endif

#ifdef WITH_FIELDML
#  define ASSERT_WITH_FIELDML() !Do nothing
#else
#  define ASSERT_WITH_FIELDML() \
   CALL FlagError("Must compile with WITH_FIELDML ON to use FieldML functionality.",err,error,*999)
#endif

#ifdef WITH_PETSC
#  define ASSERT_WITH_PETSC() !Do nothing
#else
#  define ASSERT_WITH_PETSC() \
   CALL FlagError("Must compile with WITH_PETSC ON to use PETSc functionality.",err,error,*999)
#endif

