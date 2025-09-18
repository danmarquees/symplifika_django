# Integração com Google Gemini (IA) no Symplifika

Este documento explica como configurar e utilizar a integração com a API Google Gemini para expandir atalhos de texto inteligentes com inteligência artificial.

---

## 1. O que é Gemini?

Google Gemini é uma API de IA generativa capaz de criar, expandir e melhorar textos automaticamente. No Symplifika, você pode usar Gemini para gerar conteúdos dinâmicos, propostas comerciais, respostas automáticas, e muito mais.

---

## 2. Como configurar a chave Gemini

1. **Obtenha sua chave de API Gemini**  
   - Acesse [Google AI Studio](https://aistudio.google.com/) ou o painel de desenvolvedor Gemini.
   - Crie um projeto e gere uma chave de API.

2. **Adicione a chave ao seu arquivo `.env`**  
   Na raiz do projeto, inclua:
   ```
   GEMINI_API_KEY=coloque_sua_chave_aqui
   ```

3. **Verifique se o backend está lendo a variável**  
   O arquivo `settings.py` já está preparado para ler `GEMINI_API_KEY`.

---

## 3. Como usar Gemini nos atalhos

Ao criar ou editar um atalho, selecione o tipo de expansão `ai_enhanced` e forneça um prompt de IA.

**Exemplo de payload para criar atalho com IA:**

```json
{
  "trigger": "//proposta",
  "title": "Proposta Comercial",
  "content": "Proposta para desenvolvimento de sistema.",
  "expansion_type": "ai_enhanced",
  "ai_prompt": "Expanda em uma proposta comercial completa e profissional"
}
```

---

## 4. Fluxo de uso

1. O usuário aciona o atalho com expansão IA.
2. O backend envia o conteúdo e o prompt para a API Gemini.
3. Gemini retorna o texto expandido.
4. O usuário vê o resultado pronto para uso.

---

## 5. Exemplo de chamada à API Gemini (Python)

```python
import google.generativeai as genai

genai.configure(api_key="SUA_CHAVE_GEMINI")

model = genai.GenerativeModel("gemini-pro")
response = model.generate_content("Expanda em uma proposta comercial completa e profissional")
print(response.text)
```

---

## 6. Limites e boas práticas

- **Limite de requisições:** Respeite o plano contratado na Google.
- **Prompt claro:** Quanto mais específico o prompt, melhor o resultado.
- **Valide o conteúdo:** Sempre revise textos gerados por IA antes de enviar a clientes.

---

## 7. Debug e erros comuns

- **Chave inválida:** Verifique se a chave está correta no `.env`.
- **Limite excedido:** Veja o painel Gemini para seu plano.
- **Timeout:** Tente simplificar o prompt ou dividir o texto.

---

## 8. Referências

- [Google Gemini API Docs](https://ai.google.dev/)
- [Symplifika README](../README.md)
- [Exemplos de uso da API](api.md)

---

Dúvidas? Abra uma issue ou envie para o suporte Symplifika!