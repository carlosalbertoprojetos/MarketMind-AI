# Sistema Multi-Agente

O projeto agora inclui um sistema multi-agente em `ia_pipeline/agents/` com:

- `base_agent.py`
- `architect_agent.py`
- `dev_agent.py`
- `qa_agent.py`
- `growth_agent.py`
- `orchestrator_agent.py`

A memoria compartilhada fica em `ia_pipeline/agent_memory/`.

## Execucao

CLI:

```bash
py -3 scripts/run-multi-agent-pipeline.py "https://example.com" instagram --objective branding --max-cycles 2
```

API:

- `POST /campaign/multi-agent`

## Fluxo

1. `architect_agent` gera o plano tecnico.
2. `dev_agent` executa o pipeline autonomo.
3. `qa_agent` valida a saida.
4. `growth_agent` otimiza conteudos quando QA aprova.
5. `orchestrator_agent` coordena os ciclos, salva memoria e interrompe no limite configurado.

## ENV relevantes

- `MARKETINGAI_AGENT_MAX_CYCLES`
- `MARKETINGAI_AGENT_DEBUG`
- `MARKETINGAI_AUTO_PUBLISH_DEFAULT`
