# Communication API
- Frontend request data from backend, backend serve via JSON
- Data manipulation done in backend
- Abstracted metadata layer

## RESTful API contract
- GET    /api/folders            → returns folder structure
- POST   /api/tags               → adds a tag to a file
- GET    /api/files?tag=audio    → returns files with "audio" tag

## What is REST?
* Architectural style
* Six principles:
    - Uniform Interface
    - Client-Server
    - Stateless
    - Cacheable
    - Layered System
    - Code on Demand (Optional)

### Uniform Interface
* **Identification of resources** -- The interface must uniquely identify each resource involved in the interaction between the client and the server.
* **Manipulation of resources through representations** -- The resources should have uniform representations in the server response. 
API consumers should use these representations to modify the resource state in the server.
* **Self-descriptive messages** -- Each resource representation should carry enough information to describe how to process the message. 
It should also provide information on the additional actions that the client can perform on the resource.
* **Hypermedia as the engine of application state** -- The client should have only the initial URI of the application. The client application should dynamically drive all other resources and interactions with the use of hyperlinks.

### Client-Server
* Enforces separation of concerns
* Leads to better portability
### Stateless
* Each request from client to server must contain all information necessary to understand and complete the request.
* *How does this affect json metadata?*
### Cacheable
* Response should implicitly or explicitly label itself as cacheable or non-cacheable.
### Layered System
* Allows architecture to be composed of hierarchical layers.
* Each component can't see beyond the immideate layer they are interacting with.


