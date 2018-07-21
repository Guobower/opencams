# Open Community Management

## Introduction

This module aims to implement a community management platform that will be extensible in many different community management modules always using REM as a base dependency.

## Installing


Install Odoo community edition server version 11.0 and OpenCAMS modules.

```bash
git clone --single-branch --branch 11.0 --depth 1 https://github.com/odoo/odoo 11.0

git clone https://gitlab.com/opencams/opencams.git opencams

./11.0/odoo-bin --addons-path ./11.0/addons,./custom -i opencams,opencams_enforce

```

## Getting Started

Open "My Community" >> "Units" and press "Create" to create your first unit