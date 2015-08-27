B = 1

def zero():
    print "You typed zero.\n"

def sqr():
    print "You typed one.\n"

switch = {0 : zero, 1 : sqr}

switch[B]()

print "You typed zero.\n"
