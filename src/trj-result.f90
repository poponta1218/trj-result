module trj_result
  implicit none
  private

  public :: say_hello
contains
  subroutine say_hello
    print *, "Hello, trj-result!"
  end subroutine say_hello
end module trj_result
