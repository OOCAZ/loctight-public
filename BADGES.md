# GitHub Actions Status Badges

Once you push these changes and the GitHub Actions workflows run successfully, you can add these badges to your README.md:

## Test Status Badge

```markdown
![Tests](https://github.com/OOCAZ/loctight-public/actions/workflows/tests.yml/badge.svg)
```

## Lint Status Badge

```markdown
![Lint](https://github.com/OOCAZ/loctight-public/actions/workflows/lint.yml/badge.svg)
```

## Combined (for top of README)

Add these lines near the top of your README.md:

```markdown
# LOCTight

![Tests](https://github.com/OOCAZ/loctight-public/actions/workflows/tests.yml/badge.svg)
![Lint](https://github.com/OOCAZ/loctight-public/actions/workflows/lint.yml/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple, open-source program to keep your PC active and open for a specified amount of time...
```

These badges will show:

- ✅ Green check if tests/linting pass
- ❌ Red X if tests/linting fail
- 🟡 Yellow dot if tests/linting are running

The badges automatically update when you push changes!
