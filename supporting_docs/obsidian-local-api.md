Of course. Here is the provided Swagger UI documentation converted into a clean Markdown format.

***

# Local REST API for Obsidian v1.0

You can use this interface for trying out your Local REST API in Obsidian.

Before trying the below tools, you will want to make sure you press the "Authorize" button below and provide the API Key you are shown when you open the "Local REST API" section of your Obsidian settings. All requests to the API require a valid API Key; so you won't get very far without doing that.

When using this tool you may see browser security warnings due to your browser not trusting the self-signed certificate the plugin will generate on its first run. If you do, you can make those errors disappear by adding the certificate as a "Trusted Certificate" in your browser or operating system's settings.

## Servers

The API is available via the following base URLs:
- `https://127.0.0.1:27124` - HTTPS (Secure Mode)
- `http://127.0.0.1:27124` - HTTP (Insecure Mode)

## Authentication
All requests (except for `GET /`) require an API key to be sent in the `Authorization` header as a Bearer token.
- **Header:** `Authorization: Bearer YOUR_API_KEY`

---

## System

Endpoints for getting server and system information.

### `GET /`
Returns basic details about the server.

Returns basic details about the server as well as your authentication status. This is the only API request that does *not* require authentication.

#### Responses
<details>
<summary><strong><code>200 Success</code></strong></summary>

**Example Response** `application/json`
```json
{
  "authenticated": true,
  "service": "obsidian-local-rest-api",
  "versions": {
    "obsidian": "1.5.3",
    "self": "3.0.0"
  }
}
```
</details>

### `GET /obsidian-local-rest-api.crt`
Returns the certificate in use by this API.

#### Responses
<details>
<summary><strong><code>200 Success</code></strong></summary>
Returns the certificate file.
</details>

### `GET /openapi.yaml`
Returns OpenAPI YAML document describing the capabilities of this API.

#### Responses
<details>
<summary><strong><code>200 Success</code></strong></summary>
Returns the OpenAPI specification in YAML format.
</details>

---

## Active File
Endpoints for interacting with the currently active file in the Obsidian UI.

### `DELETE /active/`
Deletes the currently-active file in Obsidian.

#### Responses
<details>
<summary><strong><code>204 Success</code></strong></summary>
The file was successfully deleted.
</details>
<details>
<summary><strong><code>404 Not Found</code></strong></summary>
The active file does not exist.
</details>
<details>
<summary><strong><code>405 Method Not Allowed</code></strong></summary>
The active item is a directory, not a file.
</details>

### `GET /active/`
Return the content of the active file open in Obsidian.

Returns the content of the currently active file in Obsidian. If you specify the header `Accept: application/vnd.olrapi.note+json`, it will return a JSON representation of your note including parsed tag and frontmatter data as well as filesystem metadata.

#### Responses
<details>
<summary><strong><code>200 Success</code></strong></summary>

**Content-Type:** `text/markdown`
Returns the raw markdown content of the note.

**Content-Type:** `application/vnd.olrapi.note+json`
```json
{
  "content": "string",
  "frontmatter": {},
  "path": "string",
  "stat": {
    "ctime": 0,
    "mtime": 0,
    "size": 0
  },
  "tags": [
    "string"
  ]
}
```
</details>
<details>
<summary><strong><code>404 Not Found</code></strong></summary>
No active file exists or is open.
</details>

### `PATCH /active/`
Partially update content in the currently open note.

Inserts content into the currently-open note relative to a heading, block reference, or frontmatter field within that document.

#### Headers

| Name | Type | Required | Description |
|---|---|---|---|
| `Operation` | string | **Yes** | Patch operation to perform. <br>_Available values_: `append`, `prepend`, `replace` |
| `Target-Type` | string | **Yes** | Type of target to patch. <br>_Available values_: `heading`, `block`, `frontmatter` |
| `Target` | string | **Yes** | Target to patch (e.g., the heading text, block ID, or frontmatter key). This value must be URL-Encoded if it includes non-ASCII characters. |
| `Target-Delimiter` | string | No | Delimiter to use for nested targets (i.e. Headings). <br>_Default_: `::` |
| `Trim-Target-Whitespace` | boolean | No | Trim whitespace from Target before applying patch? <br>_Default_: `false` |

#### Request Body
Content you would like to insert. Can be `text/markdown` or `application/json`.

#### Responses
<details>
<summary><strong><code>200 Success</code></strong></summary>
The patch operation was successful.
</details>
<details>
<summary><strong><code>400 Bad Request</code></strong></summary>
The request was malformed. See the response message for details.
</details>
<details>
<summary><strong><code>404 Not Found</code></strong></summary>
The target (heading, block, etc.) does not exist in the active file.
</details>

### `POST /active/`
Append content to the active file open in Obsidian.

Appends content to the end of the currently-open note. If you would like to insert text relative to a particular heading instead of appending to the end of the file, see the `PATCH` endpoint.

#### Request Body
**Content-Type:** `text/markdown`
```markdown
# This is my document

something else here
```

#### Responses
<details>
<summary><strong><code>204 Success</code></strong></summary>
The content was successfully appended.
</details>
<details>
<summary><strong><code>400 Bad Request</code></strong></summary>
The request was malformed.
</details>

### `PUT /active/`
Update the content of the active file open in Obsidian. This will replace the entire content of the file.

#### Request Body
**Content-Type:** `text/markdown` or `*/*`
The full content of the file you would like to upload.

#### Responses
<details>
<summary><strong><code>204 Success</code></strong></summary>
The file content was successfully replaced.
</details>
<details>
<summary><strong><code>400 Bad Request</code></strong></summary>
Incoming file could not be processed.
</details>

---

## Commands
Endpoints for listing and executing Obsidian commands.

### `GET /commands/`
Get a list of available commands.

#### Responses
<details>
<summary><strong><code>200 Success</code></strong></summary>

**Example Response** `application/json`
```json
{
  "commands": [
    {
      "id": "global-search:open",
      "name": "Search: Search in all files"
    },
    {
      "id": "graph:open",
      "name": "Graph view: Open graph view"
    }
  ]
}
```
</details>

### `POST /commands/{commandId}/`
Execute a command.

#### Path Parameters
| Name | Type | Required | Description |
|---|---|---|---|
| `commandId` | string | **Yes** | The ID of the command to execute (e.g., `graph:open`). |

#### Responses
<details>
<summary><strong><code>204 Success</code></strong></summary>
The command was executed successfully.
</details>
<details>
<summary><strong><code>404 Not Found</code></strong></summary>
The command ID specified does not exist.
</details>

---

## Open
Endpoints for opening files in the Obsidian UI.

### `POST /open/{filename}`
Open the specified document in the Obsidian user interface. Note: Obsidian will create a new document at the path you have specified if such a document did not already exist.

#### Path Parameters
| Name | Type | Required | Description |
|---|---|---|---|
| `filename` | string | **Yes** | Path to the file to open (relative to your vault root). |

#### Query Parameters
| Name | Type | Required | Description |
|---|---|---|---|
| `newLeaf` | boolean | No | If `true`, opens the file in a new leaf (tab/pane). |

#### Responses
<details>
<summary><strong><code>200 Success</code></strong></summary>
The file was successfully opened.
</details>

---

## Periodic Notes
Endpoints for interacting with periodic notes (requires the Periodic Notes community plugin).

### `GET /periodic/{period}/`
Get the current periodic note for the specified period.

#### Path Parameters
| Name | Type | Required | Description |
|---|---|---|---|
| `period` | string | **Yes** | The period to get. <br>_Available values_: `daily`, `weekly`, `monthly`, `quarterly`, `yearly` |

#### Responses
Identical to the `GET /active/` endpoint, returning either raw markdown or a JSON object based on the `Accept` header.
<details>
<summary><strong><code>200 Success</code></strong></summary>
...
</details>
<details>
<summary><strong><code>404 Not Found</code></strong></summary>
...
</details>

### `POST /periodic/{period}/`
Append content to the current periodic note for the specified period. Note that this will create the relevant periodic note if necessary.

#### Path Parameters
| Name | Type | Required | Description |
|---|---|---|---|
| `period` | string | **Yes** | The period to append to. <br>_Available values_: `daily`, `weekly`, `monthly`, `quarterly`, `yearly` |

#### Request Body
**Content-Type:** `text/markdown`
The content you would like to append.

#### Responses
<details>
<summary><strong><code>204 Success</code></strong></summary>
The content was successfully appended.
</details>
<details>
<summary><strong><code>400 Bad Request</code></strong></summary>
...
</details>

### `GET /periodic/{period}/{year}/{month}/{day}/`
Get the periodic note for the specified period and date.

#### Path Parameters
| Name | Type | Required | Description |
|---|---|---|---|
| `period` | string | **Yes** | The period to get. <br>_Available values_: `daily`, `weekly`, `monthly`, `quarterly`, `yearly` |
| `year` | number | **Yes** | The year of the date. |
| `month` | number | **Yes** | The month (1-12) of the date. |
| `day` | number | **Yes** | The day (1-31) of the date. |

#### Responses
Identical to `GET /periodic/{period}/`.
<details>
<summary><strong><code>200 Success</code></strong></summary>
...
</details>
<details>
<summary><strong><code>404 Not Found</code></strong></summary>
...
</details>

### Other Periodic Notes Endpoints
The following endpoints are also available and function identically to their `/active/` or `/vault/{filename}` counterparts, but operate on the specified periodic note.

- **`DELETE /periodic/{period}/`**: Delete the current periodic note.
- **`PATCH /periodic/{period}/`**: Partially update the current periodic note.
- **`PUT /periodic/{period}/`**: Replace the content of the current periodic note.
- **`DELETE /periodic/{period}/{year}/{month}/{day}/`**: Delete the periodic note for a specific date.
- **`PATCH /periodic/{period}/{year}/{month}/{day}/`**: Partially update the periodic note for a specific date.
- **`POST /periodic/{period}/{year}/{month}/{day}/`**: Append to the periodic note for a specific date.
- **`PUT /periodic/{period}/{year}/{month}/{day}/`**: Replace the content of the periodic note for a specific date.

---

## Search
Endpoints for searching your vault.

### `POST /search/`
Search for documents matching a specified search query. This endpoint supports multiple query formats based on the `Content-Type` header.

#### Request Body
**Content-Type:** `application/vnd.olrapi.dataview.dql+txt`
Accepts a `TABLE`-type Dataview query as a text string.
```
TABLE
  time-played AS "Time Played",
  length AS "Length",
  rating AS "Rating"
FROM #game
SORT rating DESC
```
**Content-Type:** `application/vnd.olrapi.jsonlogic+json`
Accepts a JsonLogic query specified as JSON.

#### Responses
<details>
<summary><strong><code>200 Success</code></strong></summary>
Returns an array of matching files.

**Example Response** `application/json`
```json
[
  {
    "filename": "path/to/my/note.md",
    "result": {
      "Time Played": "10 hours",
      "Length": "Long",
      "Rating": "5/5"
    }
  }
]
```
</details>
<details>
<summary><strong><code>400 Bad Request</code></strong></summary>
Bad request. Make sure you have specified an acceptable `Content-Type` for your search query.
</details>

### `POST /search/simple/`
Search for documents matching a specified text query.

#### Query Parameters
| Name | Type | Required | Description |
|---|---|---|---|
| `query` | string | **Yes** | Your search query. |
| `contextLength` | number | No | How much context to return around the matching string. _Default_: `100` |

#### Responses
<details>
<summary><strong><code>200 Success</code></strong></summary>

**Example Response** `application/json`
```json
[
  {
    "filename": "path/to/file.md",
    "score": 0.987,
    "matches": [
      {
        "context": "...some text around the match result...",
        "match": {
          "start": 123,
          "end": 130
        }
      }
    ]
  }
]
```
</details>

---

## Vault Directories
Endpoints for listing the contents of directories in your vault.

### `GET /vault/`
List files that exist in the root of your vault.

#### Responses
<details>
<summary><strong><code>200 Success</code></strong></summary>

**Example Response** `application/json`
```json
{
  "files": [
    "mydocument.md",
    "somedirectory/"
  ]
}
```
</details>
<details>
<summary><strong><code>404 Not Found</code></strong></summary>
Directory does not exist.
</details>

### `GET /vault/{pathToDirectory}/`
List files that exist in the specified directory.

#### Path Parameters
| Name | Type | Required | Description |
|---|---|---|---|
| `pathToDirectory` | string | **Yes** | Path to list files from (relative to your vault root). Note that empty directories will not be returned. |

#### Responses
Identical to `GET /vault/`.
<details>
<summary><strong><code>200 Success</code></strong></summary>
...
</details>
<details>
<summary><strong><code>404 Not Found</code></strong></summary>
...
</details>

---

## Vault Files
Endpoints for CRUD operations on specific files in your vault.

### `DELETE /vault/{filename}`
Delete a particular file in your vault.

#### Path Parameters
| Name | Type | Required | Description |
|---|---|---|---|
| `filename` | string | **Yes** | Path to the relevant file (relative to your vault root). |

#### Responses
<details>
<summary><strong><code>204 Success</code></strong></summary>
The file was successfully deleted.
</details>
<details>
<summary><strong><code>404 Not Found</code></strong></summary>
...
</details>
<details>
<summary><strong><code>405 Method Not Allowed</code></strong></summary>
Your path references a directory instead of a file.
</details>

### `GET /vault/{filename}`
Return the content of a single file in your vault.

#### Path Parameters
| Name | Type | Required | Description |
|---|---|---|---|
| `filename` | string | **Yes** | Path to the relevant file (relative to your vault root). |

#### Responses
Identical to `GET /active/`, returning raw markdown or a JSON object based on the `Accept` header.
<details>
<summary><strong><code>200 Success</code></strong></summary>
...
</details>
<details>
<summary><strong><code>404 Not Found</code></strong></summary>
...
</details>

### `PATCH /vault/{filename}`
Partially update content in an existing note.

#### Path Parameters
| Name | Type | Required | Description |
|---|---|---|---|
| `filename` | string | **Yes** | Path to the relevant file (relative to your vault root). |

#### Headers
Identical to `PATCH /active/`.

#### Request Body
Identical to `PATCH /active/`.

#### Responses
<details>
<summary><strong><code>200 Success</code></strong></summary>
...
</details>
<details>
<summary><strong><code>400 Bad Request</code></strong></summary>
...
</details>
<details>
<summary><strong><code>404 Not Found</code></strong></summary>
...
</details>

### `POST /vault/{filename}`
Append content to a new or existing file. If the specified file does not yet exist, it will be created as an empty file before appending.

#### Path Parameters
| Name | Type | Required | Description |
|---|---|---|---|
| `filename` | string | **Yes** | Path to the relevant file (relative to your vault root). |

#### Request Body
**Content-Type:** `text/markdown`
The content to append.

#### Responses
<details>
<summary><strong><code>204 Success</code></strong></summary>
...
</details>
<details>
<summary><strong><code>400 Bad Request</code></strong></summary>
...
</details>

### `PUT /vault/{filename}`
Create a new file in your vault or update the content of an existing one.

#### Path Parameters
| Name | Type | Required | Description |
|---|---|---|---|
| `filename` | string | **Yes** | Path to the relevant file (relative to your vault root). |

#### Request Body
**Content-Type:** `text/markdown` or `*/*`
The full content to write to the file.

#### Responses
<details>
<summary><strong><code>204 Success</code></strong></summary>
...
</details>
<details>
<summary><strong><code>400 Bad Request</code></strong></summary>
...
</details>