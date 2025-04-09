import logging
import socket
import os

# Get environment variables for Logstash connection
LOGSTASH_HOST = os.getenv("LOGSTASH_HOST", "localhost")
LOGSTASH_PORT = int(os.getenv("LOGSTASH_PORT", 5044))

# Configure basic logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

# Create logger
logger = logging.getLogger("payment-service")

# Simple text-based TCP handler for Logstash
class SimpleTcpHandler(logging.Handler):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.socket = None
        self.connect()
        
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
        except Exception:
            self.socket = None
    
    def emit(self, record):
        if not self.socket:
            try:
                self.connect()
            except Exception:
                return
                
        if not self.socket:
            return
            
        try:
            # Format the log message
            formatted_message = self.format(record) + '\n'
            
            # Send to Logstash
            self.socket.sendall(formatted_message.encode('utf-8'))
        except Exception:
            self.socket = None  # Force reconnection next time

# Add Logstash handler if configured
if LOGSTASH_HOST and LOGSTASH_PORT:
    try:
        # Create the handler
        tcp_handler = SimpleTcpHandler(LOGSTASH_HOST, LOGSTASH_PORT)
        
        # Set a formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        tcp_handler.setFormatter(formatter)
        
        # Add to logger
        logger.addHandler(tcp_handler)
        
        # Test log
        logger.info("Logstash logging configured")
    except Exception as e:
        logger.error(f"Failed to configure Logstash logging: {str(e)}")