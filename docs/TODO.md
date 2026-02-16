# Phases
**Core solids**
1. Fix DB queries
2. Proper DB Constraints
3. Define clear responsibilities
	- db.py - db access only
	- scanner.py - filesystem scanning
	- service.py business logic (import/update)
4. Change detection
	- New files
	- modified
	- deletions
	- rename

**Minimal API**
FastAPI / Flask

**Very simple Frontend**



# Tasks
- GUI that displays current files, applies filters, and search
- API in FLASK to request actions from the backend
- 
### High priority
### Medium priority
### Low priority
# In Progress
- Detect changes to files
- Generate tags based on dir-structure
# Done
- Import files to database
- Avoid duplicates (based on Path and Hash)