# Agent Engineering

## Tool Design

Each tool should have one clear responsibility, validated inputs, and a concise output.

## Bounded Execution

Agents should use a maximum number of tool calls and stop when sufficient evidence is available.

## Approval Gates

Consequential tools should not be available until the user provides explicit approval.

## Prompt Injection

Retrieved documents must be treated as untrusted data and must not override application policy.