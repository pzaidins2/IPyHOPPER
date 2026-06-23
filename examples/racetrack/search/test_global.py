# test whether Python retains global variables during timing tests

didit = False

def foo(n,flag):
    global didit
    print('called foo({},{})'.format(n,flag))
    if didit == False:
        print('do the loop')
        didit = flag
        for i in range(1,n):
            pass
    else:
        pass
#        print('skip')

