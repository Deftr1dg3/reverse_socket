#!/usr/bin/env python3


class NotConnectedToTheTarget(Exception):
    ...
    
class NoPathProvided(Exception):
    ...

class NotEnoughArgumentsProvided(Exception):
    ...

class IncompatibleExtension(Exception):
    ...
    
class PathDoesNotExist(Exception):
    ...
    
class ClientIsNotConnected(Exception):
    ...