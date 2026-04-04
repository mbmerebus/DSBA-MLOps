# Authentication and Security

## Navigation
Go back [Main page - Readme](../README.md)
Other pages:
- [Detailed functionnalities](product.md)
- [Architecture](architecture.md)
- [Machine Learning for Property Scoring](scoring.md)

## Prerequisite
This section of the documentation tackles user data encryption in datastorage units (kinds of "simple" databases like Redis). Reading first about Redis in the [project architecture](architecture.md) section is strongly advised.

## Passwords

User passwords are not (and should never be) stored in plain text. They are encrypted (hashed) using **bcrypt** before being written to the authentication datastorage. 

Bcrypt is a one-way hashing algorithm, which means it is computationally infeasible to reverse the encrypted form to the original password, even with direct access to the database.

This is made to validate basic account security concerns.

## Data Encryption

Estimate history is stored in a dedicated Redis instance, separate from the authentication datastorage. It is encrypted with a distinct key. Having separated encryption ensures that even in the event of a partial breach, access to one datastorage does not compromise the other.

This is very relevant because estimates may contain sensitive input data. In the "naming" your estimate field, users could describe properties by address, which constitutes personally identifiable information and warrants a good degree of data security (for legal and ethical reasons).

## CORS Policy

Cross-Origin Resource Sharing (CORS) controls which domains are allowed to make requests to the API. The current configuration is permissive (`allow_origins=["*"]`) to allow the user interface to communicate with the backend during local development.

**This configuration must not be used in production.** In a production environment, CORS should be restricted to the specific domain serving the user interface, and reviewed by a security expert before deployment. This is acknowledged as a current limitation of the project.

Services affected are Authentication (`auth`), Gateway (`gateway`) and History (`history`).

## User Session and Secret Storage

The fact the user can open a session on the service is controlled by a token (a JWT token) that has a set validaity timespan. After this timespan, the token is no longer valid and the user has to reconnect. The reasoning behind user sessiosn is twofold:

- **Security**: without session control, a stolen token would be valid forever. By storing sessions in Redis with a 24-hour expiry, we can invalidate them on logout or let them expire automatically. If a token is compromised, the damage is limited by time.
- **User accountability**: since estimates are tied to a user account, we need to ensure that only the legitimate user can access their history. Session validation on every request guarantees that. 

___

The JWT signing secret is loaded from an environment variable and NOT hardcoded in the source code. A `.env.example` file is provided to document the required variables without exposing their values. 

The `.env` file is excluded from version control via `.gitignore` but created automatically by using the `python cli.py generate-env` command at the root of the directory. It will be already filled with the needed secrets so as to remove the pain point of knowing what a good secret is for the provider. This is standard practice, as some pretty well known tools like Django, Rails, and Laravel all generate secrets automatically on project initialization.