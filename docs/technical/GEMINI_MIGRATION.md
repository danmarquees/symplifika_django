# Migração da OpenAI para Google Gemini

Este documento descreve a migração do projeto Symplifika da API da OpenAI para a API do Google Gemini.

## Alterações Realizadas

### 1. Dependências
- **Removido**: `openai==1.99.9`
- **Adicionado**: `google-generativeai==0.3.2`

### 2. Configurações (settings.py)
- **Alterado**: `OPENAI_API_KEY` → `GEMINI_API_KEY`

### 3. Serviço de IA (shortcuts/services.py)
- **Cliente**: OpenAI → Google Generative AI
- **Modelo**: `gpt-3.5-turbo` → `gemini-1.5-flash`
- **Estrutura da API**: Adaptada para usar o formato do Gemini

## Configuração da API Key

### 1. Obter a API Key do Google
1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Copie a chave gerada

### 2. Configurar a Variável de Ambiente
No arquivo `.env`:
```bash
# Substituir a linha antiga
# OPENAI_API_KEY=sua_chave_openai_aqui

# Por esta nova linha
GEMINI_API_KEY=sua_chave_gemini_aqui
```

### 3. No ambiente de produção (Render)
1. Acesse o dashboard do Render
2. Vá em Environment Variables
3. Remova `OPENAI_API_KEY`
4. Adicione `GEMINI_API_KEY` com o valor da sua chave

## Diferenças na API

### Estrutura de Requisição
**OpenAI (anterior):**
```python
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."}
    ],
    max_tokens=500,
    temperature=0.7
)
content = response.choices[0].message.content
```

**Gemini (atual):**
```python
generation_config = genai.types.GenerationConfig(
    max_output_tokens=500,
    temperature=0.7,
    candidate_count=1
)

response = model.generate_content(
    prompt,
    generation_config=generation_config
)
content = response.candidates[0].content.parts[0].text
```

### Tratamento de Erros
Os erros foram adaptados para os tipos específicos do Gemini:
- **Rate limits**: Detectados por "quota" ou "limit" na mensagem
- **Autenticação**: Detectados por "authentication" ou "api_key"
- **Requisições inválidas**: Mantido "invalid"

## Modelos Disponíveis

### Gemini 1.5 Flash (atual)
- **Nome**: `gemini-1.5-flash`
- **Características**: Rápido, otimizado para tarefas diversas
- **Limite**: ~1M tokens de entrada, 8K tokens de saída

### Outros Modelos Disponíveis
- `gemini-1.5-pro`: Modelo mais poderoso, melhor para tarefas complexas
- `gemini-1.0-pro`: Versão anterior, mais estável

## Vantagens do Gemini

1. **Custo**: Geralmente mais barato que GPT-3.5-turbo
2. **Limite de tokens**: Contexto muito maior (1M tokens vs 16K)
3. **Multimodal**: Suporte nativo a imagens (para futuras funcionalidades)
4. **Performance**: Velocidade comparável ou superior
5. **Gratuito**: Tier gratuito mais generoso

## Instalação das Dependências

```bash
# Remover pacote antigo
pip uninstall openai

# Instalar novo pacote
pip install -r requirements.txt
```

## Teste da Configuração

Execute o script de verificação:
```bash
python check_environment.py
```

Ou teste diretamente no Django shell:
```python
python manage.py shell

from shortcuts.services import AIService
service = AIService()
status = service.check_api_status()
print(status)

# Teste funcional
result = service.enhance_text("Olá, como vai?")
print(result)
```

## Funcionalidades Mantidas

Todas as funcionalidades do sistema continuam funcionando:
- ✅ Expansão de texto
- ✅ Geração de templates de email
- ✅ Sugestões de atalhos
- ✅ Verificação de status da API
- ✅ Fallbacks quando API não disponível

## Troubleshooting

### Erro: "API key not valid"
- Verifique se a GEMINI_API_KEY está configurada corretamente
- Confirme se a chave não tem espaços extras
- Teste a chave diretamente no Google AI Studio

### Erro: "Quota exceeded"
- O Gemini tem limites de uso por minuto
- Aguarde alguns minutos antes de tentar novamente
- Considere upgrade do plano se necessário

### Erro: "Model not found"
- Verifique se o modelo `gemini-1.5-flash` está disponível
- Tente usar `gemini-1.0-pro` como alternativa

## Próximos Passos

1. **Monitorar**: Acompanhe o uso da API nos primeiros dias
2. **Otimizar**: Ajuste os prompts se necessário para melhor performance
3. **Expandir**: Considere usar funcionalidades multimodais do Gemini no futuro

## Suporte

Se encontrar problemas:
1. Verifique os logs da aplicação
2. Teste a API key isoladamente
3. Consulte a [documentação oficial do Gemini](https://ai.google.dev/docs)