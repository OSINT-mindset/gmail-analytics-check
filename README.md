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

**The tool based on the template [osint-cli-tool-skeleton](https://github.com/soxoj/osint-cli-tool-skeleton)**. Read its README to explore all the available functionality.

```sh
$ ./run.py ceo@telegram.org

Target: ceo@telegram.org
Results found: 1
1) Gaia Id: 105057129383411154227
Canonical Email: ceo@telegram.org

------------------------------
Total found: 1


```

## How it works

https://twitter.com/subfnSecurity/status/1255741950914727942

See also: https://t.me/osint_mindset/62
