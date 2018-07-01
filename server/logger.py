import logging.config
import sys
import os
import yaml
import functools

class SetupLogging:
    def __init__( self ):
        loggingConfigPath = '../config/logging.yaml'
        if os.path.exists(loggingConfigPath):
            with open(loggingConfigPath, 'rt') as f:
                self.config = yaml.load(f.read())
                print(self.config['handlers']['logfile']) 
    def __enter__( self ):
        logging.config.dictConfig( self.config )
        return self
    def __exit__( self, *exc ):
        logging.shutdown()
        return False

def logged( class_ ):
    # class_.logger= logging.getLogger( class_.__qualname__ )
    class_.logger = logging.getLogger( "smr."+class_.__name__ )
    return class_

def logged_func( function ):
    @functools.wraps( function )
    def logged_function( *args, **kw):
        log = logging.getLogger("smr."+function.__name__)
        kw['logger'] = log
        log.debug("%s( %r, %r )", function.__name__, args, kw)
        result = function (*args, **kw)
        log.debug("%s = %r ", function.__name__, result)
        return result
    return logged_function
        
