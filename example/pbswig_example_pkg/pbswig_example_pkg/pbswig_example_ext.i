%module pbswig_example_ext
%{
#include "example.pb.h"
void say_it(const example::Say& it);
%}

void say_it(const example::Say& it);
