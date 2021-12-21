# Gmail Analytics Check

- Find GAIA ID for any Gmail
- Resolve any alternate email of Gmail account to the primary email

## Setup

You must do it only once for preparing `data.txt` file with long-living cookies.

1. Create a [Google Analytics project](https://analytics.google.com/analytics/web/#/).
2. Download [GHunt](https://github.com/mxrch/GHunt), run "check_and_gen"
3. Generate [cookies the most convenient way](https://github.com/mxrch/GHunt/tree/master#usage
). 
4. Сopy resources/data.txt file to path with script.

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

## How it works

https://twitter.com/subfnSecurity/status/1255741950914727942

See also: https://t.me/osint_mindset/62
