# import the protobuf model
from pbswig_example_model import example_pb

# import the extension package that uses it
import pbswig_example_pkg

# create the model object in Python
say = example_pb.Say()
say.text = "Hello PBSWIG!"

# seamlessly pass it to the C++ extension
pbswig_example_pkg.say_it(say)
