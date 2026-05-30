---
name: new-brief
description: Create a brief spec so the user can start following a research area. Use this when the user wants to add, set up, or follow a recurring brief on a topic, for example a request to follow diffusion models or to get a weekly AI-safety brief. Writes a short spec file under /briefs/specs/.
---

# New brief

Help the user set up a brief by first *understanding what they actually want*, then
writing a short spec file. The interview matters more than the file: a brief is only
useful if it tracks the right thing, framed for how the user will actually use it.

## Understand before you write
Your job here is elicitation, not form-filling. A spec is good once you understand
these five things. Infer what you can from what the user already said, and ask only
about the ones that are genuinely unclear:

1. **The job to be done (the why).** What is the user trying to stay on top of, and
   what will they *do* with the brief — make a decision, learn a field, track a
   competitor, find papers to read? This shapes everything else; lead with it.
2. **Topic and boundaries.** The subject, and what's in vs out. "Diffusion models"
   could mean only sampling, or include flow matching, video, theory. Pin the edges.
3. **The angle.** Which aspect matters — new methods, empirical results, real-world
   applications, SOTA on a benchmark, one specific open problem?
4. **What to skip.** The noise they don't want: pure theory, incremental tweaks,
   surveys, a subfield they already follow elsewhere.
5. **Depth and audience.** One-line skim vs short annotations, and who's reading —
   their expertise level and the tone (practitioner, researcher, newcomer).

## How to ask
- **Ask only for real gaps.** If the user already implied something, don't re-ask
  it — reflect it back instead. Interrogating someone who was already clear is worse
  than asking nothing.
- **Lead with the why.** If you only get to ask one thing, ask what they will use the
  brief for. A good answer here lets you infer or default most of the rest.
- **Small batches, with defaults.** Ask one to three focused questions at a time,
  each carrying a sensible default ("...or should I include video diffusion too?"),
  so the user can confirm quickly instead of composing an essay.
- **Reflect, then confirm.** Before writing, play back a one-line summary of the brief
  you are about to create and let the user correct it. Stop asking once you understand
  the five things above — over-asking is its own failure.

## Write the spec
- Slug: a short kebab-case id from the topic, e.g. "Diffusion Models" ->
  `diffusion-models`. It becomes the brief's id and its output folder name.
- List `/briefs/specs/` first. If the slug already exists, ask whether to update it
  rather than overwrite it silently.
- Write `/briefs/specs/<slug>.md` as a **short** free-form spec: a title plus ~3–6
  lines of plain prose capturing the five things above. It is read, not parsed. A
  spec is a short description, not a requirements document — distill what you learned,
  don't paste back everything the user said.
- Tell the user what you created and that the next brief run will pick it up.

## Example spec — the right length

```
# Diffusion models

For a practitioner shipping image models: new work on diffusion and flow-based
generation, focused on sampling efficiency and guidance. Skip pure theory and
incremental tweaks. One line per paper, with why it matters.
```
