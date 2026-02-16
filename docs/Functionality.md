# File Manager / Database
This app is an abstraction layer over files, optimized for workflows. 
	The filesystem tells you where a file is.
	The file itself tells you what it is.
	This app tells you what it means.
Manage and structure files like audio and media. Add tags to files to add them to categories. Add new file structure within the category to work with the files better based on the current use case.
Option to keep some kind of directory structure when selecting a category

## Tag Types
Hierarchical tags - Different tags have different importance
- Free tags, set by users
- Predefined tags
- Namespaced tags?
		- genre:folk + context:concert
- Structure tags

## Workflow Profile
- Create Presets of tag combinations, viewing settings etc

## Categorization questions
- Of what rough category is this file?
- What is the use case of this file?
- What is the quality of this file?
- Album? -> Name, Order nr.
- What does "same file" mean? Detecting duplicates

## File Identification
What is considered the same file?
- Path - Changed when moved
- Name - Renaming
- Inode / file ID - OS-specific, change on copy but survives renames
- Hash - Detect identical content and content change
- File size + modified time
### Layered identity
**Primary ID** - SQLite id
- Never changes
- Used internally
**Content identity** - hash
- Detect duplicates
- Detect content change
**Location hints** - current path / inode / file ID
- Detect renames
- Track moves


## Core Concepts
#### Audio recordings

#### Photo
#### Video
## Optional Extra Functionality
- Add notes to a file
- Link files, sheet music + audio
- Versioning files, for production?
- Export files by tags