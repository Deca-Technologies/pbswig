#include <iostream>
#include "example.pb.h"

void say_it(const example::Say& it)
{
    std::cout << it.text() << "\n";
}

