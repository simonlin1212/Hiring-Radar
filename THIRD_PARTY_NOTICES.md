# Third-party notices

Hiring Radar is MIT-licensed. It borrows from, or talks to, the projects below.

## openroles (code) — MIT

`radar/ats/workday.py` ports the Workday career-site discovery logic (robots.txt site scoring) from
openroles, and several adapters in `radar/ats/` follow the public endpoints that openroles documents
(Pinpoint, Manatal, Rippling, Hireology, ApplicantPro/isolved Hire, UKG UltiPro, Teamtailor, Zoho Recruit,
JazzHR, CareerPlug, Jobvite, iCIMS, PageUp). Source: https://github.com/datascry/openroles

```
MIT License

Copyright (c) 2026 datascry

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## openroles dataset (company directory) — CC BY-SA 4.0

`--directory-update` downloads openroles' tenant lists (which company uses which hiring system) to
`~/.hiring-radar/directory/` on your machine. The data is **not** bundled in this repository.
Attribution: openroles dataset © 2026 datascry, licensed under CC BY-SA 4.0
(https://creativecommons.org/licenses/by-sa/4.0/). If you redistribute the downloaded directory,
the same license applies to it.

## freehire — MIT

The `freehire` board reads freehire's public API (https://freehire.me, https://github.com/strelov1/freehire)
under its terms: public API only, no scraping around it, no rate-limit evasion. No freehire code is copied.

```
MIT License

Copyright (c) 2026 freehire contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Public job APIs

Government and job-board APIs (JobTech/Arbetsförmedlingen, MyCareersFuture, Bundesagentur für Arbeit,
Reed, Adzuna, USAJOBS, and the remote boards) are used through their public interfaces under each
provider's own terms. Job data belongs to the employers and the providers.
