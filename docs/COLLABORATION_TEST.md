# Collaborator Push Test

Use this before real development so every teammate proves their GitHub access without touching project code.

## Goal

Each teammate must demonstrate that they can:

1. Clone/pull the repository.
2. Read `develop`.
3. Create their own test branch.
4. Add one harmless file.
5. Commit it.
6. Push the branch.
7. Open a Pull Request targeting `develop`.

## Test Procedure

Replace `<github-username>` with your actual GitHub username.

```bash
git clone https://github.com/omghotekar01-dotcom/KURUKSHETRA-2.O.git
cd KURUKSHETRA-2.O

git checkout develop
git pull origin develop

git checkout -b test/<github-username>-access
```

Create this file:

```text
collab-tests/<github-username>.md
```

Contents:

```text
GitHub username: <github-username>
Collaboration test: PASS
Date: 2026-09-11
```

Then:

```bash
git add collab-tests/<github-username>.md
git commit -m "test(collab): verify <github-username> repository access"
git push -u origin test/<github-username>-access
```

Now open a Pull Request:

```text
FROM: test/<github-username>-access
TO:   develop
```

PR title:

```text
test(collab): verify <github-username> repository access
```

## Pass Criteria

A teammate passes the collaboration test only if:

- branch push succeeds
- branch appears on GitHub
- test file appears in that branch
- PR can be opened against `develop`

The PR does NOT need to be merged immediately. Once verified, it may be merged or closed depending on team preference.

## If Push Is Rejected

Do not change project code. Check:

- correct GitHub account is signed in
- teammate accepted the repository collaborator invitation
- remote URL points to the correct repository
- GitHub credential/token has write access

Repository URL:

```text
https://github.com/omghotekar01-dotcom/KURUKSHETRA-2.O
```

## Safety

Never test collaborator permissions by editing `main`, deleting files, force-pushing, or changing real project modules.
