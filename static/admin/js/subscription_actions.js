// JavaScript para ações de assinatura no painel admin

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function cancelSubscription(subscriptionId) {
    if (!confirm('Tem certeza que deseja cancelar esta assinatura?')) {
        return;
    }

    const csrftoken = getCookie('csrftoken');

    fetch('/admin/subscription/cancel/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            subscription_id: subscriptionId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Assinatura cancelada com sucesso!');
            location.reload();
        } else {
            alert('Erro ao cancelar assinatura: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao cancelar assinatura. Verifique o console para mais detalhes.');
    });
}

function reactivateSubscription(subscriptionId) {
    if (!confirm('Tem certeza que deseja reativar esta assinatura?')) {
        return;
    }

    const csrftoken = getCookie('csrftoken');

    fetch('/admin/subscription/reactivate/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            subscription_id: subscriptionId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Assinatura reativada com sucesso!');
            location.reload();
        } else {
            alert('Erro ao reativar assinatura: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao reativar assinatura. Verifique o console para mais detalhes.');
    });
}

function syncSubscriptionStatus(subscriptionId) {
    const csrftoken = getCookie('csrftoken');

    fetch('/admin/subscription/sync/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            subscription_id: subscriptionId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Status sincronizado com sucesso!');
            location.reload();
        } else {
            alert('Erro ao sincronizar status: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao sincronizar status. Verifique o console para mais detalhes.');
    });
}

// Adicionar botões de ação dinamicamente quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    // Adicionar estilos CSS para os botões
    const style = document.createElement('style');
    style.textContent = `
        .subscription-action-btn {
            display: inline-block;
            padding: 4px 8px;
            margin: 2px;
            font-size: 11px;
            font-weight: bold;
            text-decoration: none;
            border: 1px solid;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .btn-cancel {
            background-color: #dc3545;
            color: white;
            border-color: #dc3545;
        }

        .btn-cancel:hover {
            background-color: #c82333;
            border-color: #bd2130;
            color: white;
        }

        .btn-reactivate {
            background-color: #28a745;
            color: white;
            border-color: #28a745;
        }

        .btn-reactivate:hover {
            background-color: #218838;
            border-color: #1e7e34;
            color: white;
        }

        .btn-sync {
            background-color: #007bff;
            color: white;
            border-color: #007bff;
        }

        .btn-sync:hover {
            background-color: #0056b3;
            border-color: #004085;
            color: white;
        }
    `;
    document.head.appendChild(style);

    // Adicionar funcionalidade de confirmação para ações em massa
    const actionSelect = document.querySelector('select[name="action"]');
    if (actionSelect) {
        actionSelect.addEventListener('change', function() {
            const selectedAction = this.value;
            const dangerousActions = [
                'downgrade_to_free',
                'upgrade_to_premium',
                'upgrade_to_enterprise',
                'reset_ai_usage'
            ];

            if (dangerousActions.includes(selectedAction)) {
                setTimeout(() => {
                    const goButton = document.querySelector('button[name="index"]');
                    if (goButton) {
                        goButton.onclick = function(e) {
                            const actionName = actionSelect.options[actionSelect.selectedIndex].text;
                            if (!confirm(`Tem certeza que deseja executar a ação "${actionName}" nos itens selecionados?`)) {
                                e.preventDefault();
                                return false;
                            }
                        };
                    }
                }, 100);
            }
        });
    }

    // Adicionar tooltips informativos
    const statusElements = document.querySelectorAll('[title="Status"]');
    statusElements.forEach(element => {
        element.style.cursor = 'help';
    });

    // Função para destacar linhas com problemas
    const problemStatuses = ['past_due', 'unpaid', 'canceled'];
    const rows = document.querySelectorAll('#result_list tbody tr');

    rows.forEach(row => {
        const statusCell = row.querySelector('td:nth-child(3)'); // Assumindo que status é a 3ª coluna
        if (statusCell) {
            const statusText = statusCell.textContent.toLowerCase();
            problemStatuses.forEach(problemStatus => {
                if (statusText.includes(problemStatus)) {
                    row.style.backgroundColor = '#fff3cd';
                    row.style.borderLeft = '4px solid #ffc107';
                }
            });
        }
    });
});

// Função para exportar dados de assinatura (se necessário)
function exportSubscriptionData() {
    const selectedIds = [];
    const checkboxes = document.querySelectorAll('input[name="_selected_action"]:checked');

    checkboxes.forEach(checkbox => {
        selectedIds.push(checkbox.value);
    });

    if (selectedIds.length === 0) {
        alert('Selecione pelo menos uma assinatura para exportar.');
        return;
    }

    const url = '/admin/subscription/export/?ids=' + selectedIds.join(',');
    window.open(url, '_blank');
}

// Função para atualizar status em tempo real
function startStatusPolling() {
    setInterval(() => {
        const activeSubscriptions = document.querySelectorAll('[data-status="active"], [data-status="trialing"]');
        if (activeSubscriptions.length > 0) {
            // Aqui você pode implementar polling para verificar mudanças de status
            console.log('Verificando status das assinaturas ativas...');
        }
    }, 60000); // Verificar a cada minuto
}

// Iniciar polling se estivermos na página de assinaturas
if (window.location.pathname.includes('stripesubscription')) {
    startStatusPolling();
}
