! vim: set ft=fortran:
module kind_params
  use, intrinsic :: iso_fortran_env, only: int8, int16, int32, int64, real32, real64, real128
  implicit none
  integer, parameter :: i8 = int8
  integer, parameter :: i16 = int16
  integer, parameter :: i32 = int32
  integer, parameter :: i64 = int64
  integer, parameter :: sp = real32
  integer, parameter :: dp = real64
  integer, parameter :: qp = real128
end module kind_params
