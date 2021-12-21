# gmail-analytics-check

- Find GAIA ID for any Gmail
- Resolve any secondary email of Gmail account to primary email

## Setup

Download GHunt, make "check_and_gen" and copy resources/data.txt file to path with script.

https://github.com/mxrch/GHunt/tree/master#usage

## Usage

```sh
$ ./check.py alex@telegram.org
{
  "principal": [
    {
      "id": "users/105284625337243296778",
      "user": {
        "gaiaId": "105284625337243296778",
        "email": "telegramkotobox42@gmail.com",
        "lookupKeyEmail": "alex@telegram.org"
      }
    }
  ]
}

```