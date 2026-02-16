# Main Modules
- User interface
- Database (SQLite)
- API (FLASK?)

# UI
- Functionality / tools

# Backend (Database)
- Query, insertions and deletion with SQLite


# API
Connect requests and responses between UI and Backend
**Method**
- Set up API calls that activates actions.
- 

## Major tasks
- Base file structure underneath the application
		- Hierarchical?
		- Don't fight current filesystem
- Database searching
- Define the structure for metadata
- GUI for file management
- File System Parser
		- Scans directory structure
		- Creates tags accordingly
		- Prompts user to modify tags
		- Applies tags
- 

## Sub tasks
**Detect changes among files**
- Create a list of all files currently
- Compare with the database state
- If a hash in database does not exist in current files add it to separate list
- If a file in current files does not exist in database -> Add it to new files
- What should be compared to make sure it is the same file?
	- Hash - Most reliable for unchanged files - but more computation required
	- Path - Fast and easy - less reliable if file moved or renamed
	- ??
Method:
- Go through DB list and current files to find matching pairs
- 

**Automatically generate tags based on directories and apply them**
Use current directory structure to generate tags:
- Create a list of all files and their parent folder names
- Optional way to 


## In progress


## Done

