"""connnection.py - generic console connection."""
import logging
import pexpect
import os
import string
import sys
import threading

from abc import ABC
from util.tl_logger import TLLog,logOptions
from util.hexdump import hexDump

TLLog.config('logs/connect.log', defLogLevel=logging.INFO )

log = TLLog.getLogger( 'connect' )

class ConnectionException(Exception):
  pass

class TimeoutException(ConnectionException):
  pass

class Connect(ABC):
  """Abstract class for using pexpect."""
  spawn_command = 'ssh $user@$host'
  user = 'sjournea'
  host = 'localhost'
  pswd = ''
  prompt = r'\$'
  
  def __init__(self, **kwargs):
    self._user = kwargs.get('user', self.user)
    self._host = kwargs.get('host', self.host)
    self._pswd = kwargs.get('pswd', self.pswd)
    self._spawn_command = kwargs.get('spawn_command', self.spawn_command)
    self._prompt = kwargs.get('prompt', self.prompt)
    self._conn = None
    
  def connect(self):
    dct = {
      'user': self._user,
      'host': self._host,
    }
    spawn_command = string.Template(self._spawn_command).substitute(dct)
    self._conn = pexpect.spawn(spawn_command, encoding='utf-8')
    self._conn.logfile = open('connect.log', 'a')
    self.login()
    
  def login(self):
    log.info('login() - start')
    lst = ['password:', self.prompt]
    while True:
      index, _ = self.expect_list(lst)
      if index == 0:
        self.sendline(self.pswd)
      elif index == 1:
        break
    
  def disconnect(self):
    if self._conn:
      self.send_command('exit')
      self._conn.close()
      self._conn = None
  
  def expect(self, pattern, **kwargs):
    """Wait for match to a pattern.

    Args:
      pattern: pattern to match or a list of patterns.
    Returns:
      all data before the pattern matched.
    """
    try:
      self._conn.expect(pattern, **kwargs)
      hexDump(self._conn.before, msg='RCB', logFunc=log.info)
      hexDump(self._conn.after, msg='RCA', logFunc=log.info)
      return self._conn.before
    except (pexpect.EOF, pexpect.TIMEOUT) as ex:
      raise ConnectionException(str(ex))

  def expect_list(self, pattern_list, **kwargs):
    """Wait for match from a list of patterns.

    Args:
      pattern_list: pattern to match or a list of patterns.
    Returns:
      tuple(index match, all data before the pattern matched).
    """
    try:
      index = self._conn.expect(pattern_list, **kwargs)
      hexDump(self._conn.before, msg='RCB', logFunc=log.info)
      hexDump(self._conn.after, msg='RCA', logFunc=log.info)
      return index, self._conn.before
    except (pexpect.EOF, pexpect.TIMEOUT) as ex:
      raise ConnectionException(str(ex))
  
  def send(self, command):
    """Send a raw command without waiting for a response."""
    hexDump(command, msg='SND', logFunc=log.info)
    return self._conn.send(command)

  def sendline(self, command):
    """Send a command with line sep without waiting for a response."""
    return self.send(command + os.linesep)

  def send_command(self, command, **kwargs):
    """Send a command and wait for the defined prompt."""
    self.sendline(command)
    return self.expect(self.prompt, **kwargs)


class ConnectSSH(Connect):
  spawn_command = 'ssh $user@$host'
  user = 'ruby'
  pswd = 'frenchie'
  host = 'localhost'
  prompt = r'ruby@.*\$ '

  def disconnect(self):
    if self._conn:
      try:
        self.send_command('exit')
      except ConnectionException:
        pass
      self._conn.close()
      self._conn = None

if __name__ == '__main__':
  print('Connect test')

  thrd = threading.currentThread()
  thrd.setName( 'main' )
  log.info('Connect test start')
  ssh = None
  try:
    ssh = ConnectSSH(prompt='ruby@feanor:~\$ ')
    ssh.connect()
    while True:
      s = input('Enter command: ')
      if s == 'x':
        break
      resp = ssh.send_command(s)
      print(resp)
  finally:
    if ssh:
      ssh.disconnect()
    log.info('Connect test exit')
    TLLog.shutdown()        
  
  
