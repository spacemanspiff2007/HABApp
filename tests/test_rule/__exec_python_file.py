import json
import os
import sys

if len(sys.argv) == 1:
    print(json.dumps({'cwd': os.getcwd()}))
else:
    if sys.argv[1] == 'exit_3':
        print('Error Message 3')
        sys.exit(3)

    sys.exit('Error in module!')
