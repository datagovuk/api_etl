"""
Takes a 'CSV' with a multibyte delimiter (sigh, why?) and reads it into a
buffer, replacing the weird char with a \t.
"""
import sys
from cStringIO import StringIO

def convert_squiggle_to_tabs(filename):
    buffer = StringIO()

    print "Processing {f}".format(f=filename)
    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            for c in line:
                if ord(c) == 172:
                    buffer.write('\t')
                    continue
                buffer.write(c)
    return buffer.getvalue()

if __name__ == "__main__":
    sys.stdout.write(convert_squiggle_to_tabs(sys.argv[1]))