import platform, shellescape, subprocess, sys

class CommandOutput(object):
	"""
	Helper class to wrap the output of Utility.capture()
	"""
	def __init__(self, returncode, stdout, stderr):
		self.returncode = returncode
		self.stdout = stdout
		self.stderr = stderr


class Utility:
	"""
	Provides utility functionality
	"""
	
	@staticmethod
	def printStderr(*args, **kwargs):
		"""
		Prints to stderr instead of stdout
		"""
		print(*args, file=sys.stderr, **kwargs)
	
	@staticmethod
	def readFile(filename):
		"""
		Reads data from a file
		"""
		with open(filename, 'rb') as f:
			return f.read().decode('utf-8')
	
	@staticmethod
	def writeFile(filename, data):
		"""
		Writes data to a file
		"""
		with open(filename, 'wb') as f:
			f.write(data.encode('utf-8'))
	
	@staticmethod
	def patchFile(filename, replacements):
		"""
		Applies the supplied list of replacements to a file
		"""
		patched = Utility.readFile(filename)
		
		# Perform each of the replacements in the supplied dictionary
		for key in replacements:
			patched = patched.replace(key, replacements[key])
		
		Utility.writeFile(filename, patched)
	
	@staticmethod
	def forwardSlashes(paths):
		"""
		Replaces Windows directory separators with Unix separators
		"""
		return list([p.replace('\\', '/') for p in paths])
	
	@staticmethod
	def escapePathForShell(path):
		"""
		Escapes a filesystem path for use as a command-line argument
		"""
		if platform.system() == 'Windows':
			return '"{}"'.format(path.replace('"', '""'))
		else:
			return shellescape.quote(path)
	
	@staticmethod
	def join(delim, items, quotes=False):
		"""
		Joins the supplied list of strings after removing any empty strings from the list
		"""
		transform = lambda s: s
		if quotes == True:
			transform = lambda s: s if ' ' not in s else '"{}"'.format(s)
		
		stripped = list([transform(i) for i in items if len(i) > 0])
		if len(stripped) > 0:
			return delim.join(stripped)
		return ''
	
	@staticmethod
	def findArgs(args, prefixes):
		"""
		Extracts the list of arguments that start with any of the specified prefix values
		"""
		return list([
			arg for arg in args
			if len([p for p in prefixes if arg.lower().startswith(p.lower())]) > 0
		])
	
	@staticmethod
	def getArgValue(arg):
		"""
		Returns the value component of an argument with the format `-KEY=VALUE`
		"""
		return arg.split('=', maxsplit=1)[1]
	
	@staticmethod
	def stripArgs(args, blacklist):
		"""
		Removes any arguments in the supplied list that are contained in the specified blacklist
		"""
		blacklist = [b.lower() for b in blacklist]
		return list([arg for arg in args if arg.lower() not in blacklist])
	
	@staticmethod
	def capture(command, input=None, cwd=None, shell=False, raiseOnError=False):
		"""
		Executes a child process and captures its output
		"""
		
		# Attempt to execute the child process
		# stderr is redirected to stdout
		p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=None, shell=False, universal_newlines=True)
		if input is not None: 
			p.stdin.write(input)

		lines = []
		# Propagate output to console
		for line in p.stdout:
			# newline is already part of line
			print(line, end='')
			lines.append(line)
		
		stdout = ''.join(lines)
		p.wait()

		# If the child process failed and we were asked to raise an exception, do so
		if raiseOnError == True and p.returncode != 0:
			raise Exception(
				'child process ' + str(command) +
				' failed with exit code ' + str(p.returncode) +
				'\nstdout: "' + stdout + "'")
		
		return CommandOutput(p.returncode, stdout, stdout)
	
	@staticmethod
	def run(command, cwd=None, shell=False, raiseOnError=False):
		"""
		Executes a child process and waits for it to complete
		"""
		# stderr is redirected to stdout
		p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=None, shell=False, universal_newlines=True)
		for line in p.stdout:
			# newline is already part of line
			print(line, end='')
		p.wait()

		if raiseOnError == True and p.returncode != 0:
			raise Exception('child process ' + str(command) + ' failed with exit code ' + str(p.returncode))
		return p.returncode
