# import modules used here -- sys is a very standard one
import sys, argparse, logging
from tradingcore.signalapp import SignalApp, APPCLASS_ALPHA, APPCLASS_EXO


try:
    from .settings import *
except SystemError:
    from scripts.settings import *

try:
    from .settings_local import *
except SystemError:
    try:
        from scripts.settings_local import *
    except ImportError:
        pass
    pass
import importlib

from tradingcore.swarmonlinemanager import SwarmOnlineManager
from tradingcore.messages import *
import pprint


class AlphaOnlineScript:
    def __init__(self, args, loglevel):
        self.args = args
        self.loglevel = loglevel
        self.alpha_name = args.alphaname
        logger = logging.getLogger('AlphaOnlineScript')
        logger.setLevel(loglevel)
        fh = None
        if args.logfile != '':
            # create file handler which logs even debug messages
            fh = logging.FileHandler(args.logfile)
            fh.setLevel(loglevel)

        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(loglevel)

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)


        if fh is not None:
            fh.setFormatter(formatter)
            logger.addHandler(fh)

        self.log = logger

        self.log.info('Init AlphaOnlineScript Alpha: {0}'.format(self.alpha_name))

        self.signal_app = SignalApp(self.alpha_name, APPCLASS_ALPHA, RABBIT_HOST, RABBIT_USER, RABBIT_PASSW)
        self.signal_app.send(MsgStatus("INIT", 'Initiating online alpha engine {0}'.format(self.alpha_name)))
        self.exo_app = SignalApp('*', APPCLASS_EXO, RABBIT_HOST, RABBIT_USER, RABBIT_PASSW)



    def swarm_updated_callback(self, swm):
        # Logging swarm structure information
        if self.loglevel == logging.DEBUG:
            self.log.debug('swarm_updated_callback: Swarm processed: {0}'.format(swm.name))
            last_state = swm.laststate_to_dict()
            del last_state['picked_equity']
            pp = pprint.PrettyPrinter(indent=4)

            self.log.debug('Swarm last state: \n {0}'.format(pp.pformat(last_state)))

        self.signal_app.send(MsgAlphaState(swm))

    def on_exo_quote_callback(self, appclass, appname, data_object):
        self.log.debug('on_exo_quote_callback: {0}.{1} Data: {2}'.format(appname, appclass, data_object))
        msg = MsgBase(data_object)

        # Make sure that is valid EXO quote message
        if msg.mtype == MsgEXOQuote.mtype:
            self.log.info('Processing EXO quote: {0} at {1}'.format(msg.exo_name, msg.exo_date))
            # Load strategy_context
            m = importlib.import_module(
                'scripts.alphas.alpha_{0}'.format(self.alpha_name.replace('alpha_', '').replace('.py', '')))

            # Initiate swarm from Mongo DB
            exo_name = msg.exo_name
            swmonline = SwarmOnlineManager(MONGO_CONNSTR, MONGO_EXO_DB, m.STRATEGY_CONTEXT)
            # Update and save swarm with new day data (and run callback)
            swmonline.process(exo_name, swm_callback=self.swarm_updated_callback)

    def main(self):
        """
        Application main()
        :return:
        """
        # Subscribe to rabbit MQ EXO feed
        self.exo_app.listen(self.on_exo_quote_callback)



# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="EXO Alpha online script",
        epilog="As an alternative to the commandline, params can be placed in a file, one per line, and specified on the commandline like '%(prog)s @params.conf'.",
        fromfile_prefix_chars='@')

    parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="store_true")


    parser.add_argument(
        '-L',
        '--logfile',
        help="Path to logfile",
        action="store",
        default=''
    )


    parser.add_argument('alphaname', type=str,
                        help='Alpha module name (see ./alphas/*.py files list)')



    args = parser.parse_args()

    # Setup logging
    if args.verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    script = AlphaOnlineScript(args, loglevel)
    script.main()


