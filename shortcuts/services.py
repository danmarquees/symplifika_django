from openai import OpenAI
import logging
from django.conf import settings
from typing import Optional
import time

logger = logging.getLogger(__name__)


class AIService:
    """Serviço para expansão de texto usando IA (OpenAI)"""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model_name = "gpt-3.5-turbo"
        self.max_tokens = 500
        self.temperature = 0.7

        if not self.api_key:
            logger.warning("OpenAI API key não configurada")

        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def enhance_text(self, content: str, custom_prompt: str = "") -> str:
        """
        Expande um texto usando IA

        Args:
            content: Texto original a ser expandido
            custom_prompt: Prompt customizado para instrução específica

        Returns:
            Texto expandido pela IA
        """
        if not self.api_key:
            raise Exception("API key do OpenAI não configurada")

        try:
            # Constrói o prompt
            base_prompt = self._build_base_prompt()

            if custom_prompt:
                full_prompt = f"{base_prompt}\n\nInstruções específicas: {custom_prompt}\n\nTexto a expandir: {content}"
            else:
                full_prompt = f"{base_prompt}\n\nTexto a expandir: {content}"

            # Faz a chamada para a API
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente especializado em expandir e melhorar textos de forma profissional e contextual."
                    },
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=30
            )

            enhanced_content = response.choices[0].message.content.strip()

            logger.info(f"Texto expandido com sucesso usando {self.model_name}")
            return enhanced_content

        except Exception as e:
            if "rate_limit" in str(e).lower():
                logger.error("Rate limit excedido na API do OpenAI")
                raise Exception("Limite de uso da IA temporariamente excedido. Tente novamente em alguns minutos.")
            elif "authentication" in str(e).lower():
                logger.error("Erro de autenticação com a API do OpenAI")
                raise Exception("Erro de configuração da IA. Contate o administrador.")
            elif "invalid" in str(e).lower():
                logger.error(f"Requisição inválida para a API do OpenAI: {e}")
                raise Exception("Erro na requisição de expansão de texto.")

        except Exception as e:
            logger.error(f"Erro inesperado na expansão de texto: {e}")
            raise Exception(f"Erro ao expandir texto: {str(e)}")

    def _build_base_prompt(self) -> str:
        """Constrói o prompt base para expansão de texto"""
        return """
Sua tarefa é expandir e melhorar o texto fornecido mantendo o contexto e a intenção original.

Diretrizes:
1. Mantenha o tom e estilo do texto original
2. Adicione detalhes relevantes e úteis
3. Melhore a clareza e profissionalismo
4. Se for um email, torne-o mais cordial e completo
5. Se for código, adicione comentários e melhore a estrutura
6. Se for uma resposta, torne-a mais informativa
7. Mantenha a linguagem apropriada para o contexto

O texto expandido deve ser natural e fluido.
        """.strip()

    def generate_email_template(self, purpose: str, tone: str = "profissional") -> str:
        """
        Gera um template de email baseado no propósito

        Args:
            purpose: Propósito do email (ex: "boas-vindas", "follow-up", "agradecimento")
            tone: Tom do email ("profissional", "casual", "formal")

        Returns:
            Template de email gerado
        """
        if not self.api_key:
            return self._get_fallback_email_template(purpose)

        try:
            prompt = f"""
Gere um template de email em português para o seguinte propósito: {purpose}
Tom desejado: {tone}

O template deve incluir:
- Assunto sugerido
- Saudação apropriada
- Corpo do email com placeholders para personalização (ex: {{nome}}, {{empresa}})
- Fechamento adequado
- Assinatura com placeholder

Formato:
Assunto: [assunto aqui]

[corpo do email aqui]

Seja conciso mas completo.
            """

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em comunicação empresarial e redação de emails."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=400,
                temperature=0.6
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Erro ao gerar template de email: {e}")
            return self._get_fallback_email_template(purpose)

    def _get_fallback_email_template(self, purpose: str) -> str:
        """Templates de email de fallback quando a IA não está disponível"""
        templates = {
            "boas-vindas": """
Assunto: Bem-vindo(a) à {empresa}!

Olá {nome},

É com grande prazer que damos as boas-vindas à {empresa}!

Estamos muito felizes em tê-lo(a) conosco e esperamos que esta seja uma parceria de muito sucesso.

Se tiver alguma dúvida, não hesite em entrar em contato.

Atenciosamente,
{assinatura}
            """.strip(),

            "agradecimento": """
Assunto: Obrigado!

Olá {nome},

Gostaria de expressar minha sincera gratidão por {motivo}.

Sua colaboração foi fundamental e muito apreciada.

Mais uma vez, muito obrigado!

Atenciosamente,
{assinatura}
            """.strip(),

            "follow-up": """
Assunto: Acompanhamento - {assunto}

Olá {nome},

Espero que esteja bem.

Gostaria de fazer um acompanhamento sobre {assunto} que discutimos anteriormente.

Podemos agendar uma conversa para discutir os próximos passos?

Aguardo seu retorno.

Atenciosamente,
{assinatura}
            """.strip()
        }

        return templates.get(purpose, """
Assunto: {assunto}

Olá {nome},

{conteudo}

Atenciosamente,
{assinatura}
        """.strip())

    def suggest_shortcuts(self, text: str, max_suggestions: int = 5) -> list:
        """
        Sugere possíveis atalhos baseados em um texto

        Args:
            text: Texto para analisar
            max_suggestions: Máximo de sugestões a retornar

        Returns:
            Lista de sugestões de atalhos
        """
        if not self.api_key:
            return self._get_fallback_suggestions(text)

        try:
            prompt = f"""
Analise o seguinte texto e sugira {max_suggestions} possíveis atalhos (triggers) que poderiam ser criados.

Texto: {text}

Para cada sugestão, forneça:
1. Trigger (começando com //)
2. Título descritivo
3. Breve explicação do uso

Formato da resposta:
//trigger1 - Título 1 - Explicação 1
//trigger2 - Título 2 - Explicação 2
...

Os triggers devem ser curtos, memoráveis e descritivos.
            """

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=300,
                temperature=0.8
            )

            suggestions_text = response.choices[0].message.content.strip()
            return self._parse_suggestions(suggestions_text)

        except Exception as e:
            logger.error(f"Erro ao gerar sugestões de atalhos: {e}")
            return self._get_fallback_suggestions(text)

    def _parse_suggestions(self, suggestions_text: str) -> list:
        """Parse das sugestões de atalhos retornadas pela IA"""
        suggestions = []
        lines = suggestions_text.split('\n')

        for line in lines:
            if line.strip() and line.startswith('//'):
                parts = line.split(' - ')
                if len(parts) >= 3:
                    trigger = parts[0].strip()
                    title = parts[1].strip()
                    description = ' - '.join(parts[2:]).strip()

                    suggestions.append({
                        'trigger': trigger,
                        'title': title,
                        'description': description
                    })

        return suggestions

    def _get_fallback_suggestions(self, text: str) -> list:
        """Sugestões de fallback quando a IA não está disponível"""
        word_count = len(text.split())

        if 'email' in text.lower():
            return [{
                'trigger': '//email-resp',
                'title': 'Resposta de Email',
                'description': 'Template para resposta rápida de email'
            }]
        elif 'obrigado' in text.lower() or 'agradec' in text.lower():
            return [{
                'trigger': '//agradec',
                'title': 'Agradecimento',
                'description': 'Mensagem de agradecimento padrão'
            }]
        elif word_count > 50:
            return [{
                'trigger': '//texto-longo',
                'title': 'Texto Longo',
                'description': 'Template para textos extensos'
            }]
        else:
            return [{
                'trigger': '//resposta',
                'title': 'Resposta Padrão',
                'description': 'Template de resposta genérica'
            }]

    def check_api_status(self) -> dict:
        """Verifica o status da API e configuração"""
        status_info = {
            'api_configured': bool(self.api_key),
            'model': self.model_name,
            'api_accessible': False,
            'error': None
        }

        if not self.api_key:
            status_info['error'] = 'API key não configurada'
            return status_info

        try:
            # Testa a API com uma requisição simples
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1,
                timeout=10
            )
            status_info['api_accessible'] = True

        except Exception as e:
            status_info['error'] = str(e)

        return status_info
