import google.generativeai as genai
import logging
from django.conf import settings
from typing import Optional
import time

logger = logging.getLogger(__name__)


class AIService:
    """Serviço para expansão de texto usando IA (Google Gemini)"""

    def __init__(self):
        self.api_key = getattr(settings, 'GEMINI_API_KEY', '')
        self.model_name = "gemini-1.5-flash"
        self.max_tokens = 500
        self.temperature = 0.7

        if not self.api_key:
            logger.warning("Gemini API key não configurada")
            self.model = None
        else:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                logger.info(f"AIService inicializado com sucesso usando {self.model_name}")
            except Exception as e:
                logger.error(f"Erro ao inicializar AIService: {e}")
                self.model = None

    def enhance_text(self, content: str, custom_prompt: str = "") -> str:
        """
        Expande um texto usando IA

        Args:
            content: Texto original a ser expandido
            custom_prompt: Prompt customizado para instrução específica

        Returns:
            Texto expandido pela IA
        """
        if not self.api_key or not self.model:
            logger.warning("AIService não configurado - retornando conteúdo original")
            return content

        try:
            # Constrói o prompt
            base_prompt = self._build_base_prompt()

            if custom_prompt:
                full_prompt = f"{base_prompt}\n\nInstruções específicas: {custom_prompt}\n\nTexto a expandir: {content}"
            else:
                full_prompt = f"{base_prompt}\n\nTexto a expandir: {content}"

            # Configura os parâmetros de geração
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=self.max_tokens,
                temperature=self.temperature,
                candidate_count=1
            )

            # Faz a chamada para a API
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )

            if response.candidates and response.candidates[0].content:
                enhanced_content = response.candidates[0].content.parts[0].text.strip()
                logger.info(f"Texto expandido com sucesso usando {self.model_name}")
                return enhanced_content
            else:
                logger.warning("Resposta vazia do modelo - retornando conteúdo original")
                return content

        except Exception as e:
            logger.error(f"Erro ao expandir texto com IA: {str(e)}")
            # Em caso de erro, retorna o conteúdo original
            return content

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

            generation_config = genai.types.GenerationConfig(
                max_output_tokens=400,
                temperature=0.6,
                candidate_count=1
            )

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )

            if response.candidates and response.candidates[0].content:
                return response.candidates[0].content.parts[0].text.strip()
            else:
                return self._get_fallback_email_template(purpose)

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

            generation_config = genai.types.GenerationConfig(
                max_output_tokens=300,
                temperature=0.8,
                candidate_count=1
            )

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )

            if response.candidates and response.candidates[0].content:
                suggestions_text = response.candidates[0].content.parts[0].text.strip()
                return self._parse_suggestions(suggestions_text)
            else:
                return self._get_fallback_suggestions(text)

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
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=1,
                temperature=0.1,
                candidate_count=1
            )

            response = self.model.generate_content(
                "test",
                generation_config=generation_config
            )

            if response.candidates:
                status_info['api_accessible'] = True
            else:
                status_info['error'] = 'Resposta vazia da API'

        except Exception as e:
            status_info['error'] = str(e)

        return status_info