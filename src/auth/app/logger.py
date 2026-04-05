import logging

#Simple logging pipeline
#To implement in every services to complement HTTP responses and such 
#-> Helps for debug and explainability
#Because each service runs in its own container, logs will be displayed
#via docker logs <name of container/service>

#NOTE: Since this file belongs to one service, the loggin
#can be tailored to this service needs.

def get_logger(name: str) -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s"
    )
    return logging.getLogger(name)