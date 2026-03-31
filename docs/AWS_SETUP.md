# Configuração AWS — Passo a passo manual

Guia completo para configurar todos os serviços AWS necessários para rodar o DungeonAI.

**Tempo estimado:** 15-20 minutos
**Região:** us-east-1 (N. Virginia) — obrigatório, pois Nova Canvas e Claude Haiku estão disponíveis aqui.

---

## 1. Verificar os models no Amazon Bedrock

Os models usados pelo projeto estão disponíveis diretamente no Model Catalog — não é mais necessário solicitar acesso manualmente.

1. Acesse o console AWS → procure **Amazon Bedrock**
2. No menu lateral, clique em **Model catalog**
3. Confirme que os seguintes models estão disponíveis na região **us-east-1**:
   - **Anthropic** → Claude 3.5 Haiku ✅
   - **Amazon** → Titan Image Generator V2 ✅

> Todos os models listados no Model Catalog já estão liberados para uso. Basta confirmar que aparecem na sua região.

**Como verificar:** No Model Catalog, busque pelos nomes e confirme que o botão de uso/teste está habilitado.

---

## 2. Criar a tabela no DynamoDB

A tabela armazena o game state (HP, inventário, localização, histórico) de cada sessão.

1. Acesse o console AWS → procure **DynamoDB**
2. Clique em **Create table**
3. Configure:
   - **Table name:** `dungeonai-game-sessions`
   - **Partition key:** `session_id` (tipo: String)
   - Deixe **Sort key** em branco
4. Em **Table settings**, selecione **Customize settings**
5. Em **Read/write capacity settings**, selecione **On-demand**
   - Isso garante que você paga apenas pelo que usar (centavos para teste)
6. Deixe o resto padrão e clique **Create table**

**Como verificar:** Clique na tabela criada → aba **Explore table items** → deve estar vazia.

---

## 3. Criar o bucket S3

O bucket armazena as imagens geradas pelo Nova Canvas a cada turno.

1. Acesse o console AWS → procure **S3**
2. Clique em **Create bucket**
3. Configure:
   - **Bucket name:** `dungeonai-scenes`
     > Se o nome já estiver em uso (S3 é global), use `dungeonai-scenes-SEU_ACCOUNT_ID`
     > e atualize o nome no arquivo `agent/tools/generate_scene.py` na variável `S3_BUCKET`
   - **Region:** US East (N. Virginia) us-east-1
4. Em **Block Public Access**, deixe **tudo marcado** (bloqueado)
   - As imagens são acessadas pelo backend via SDK, não precisam ser públicas
5. Deixe o resto padrão e clique **Create bucket**

**Como verificar:** Abra o bucket → deve estar vazio → após o primeiro turno do jogo, vai aparecer uma pasta `sessions/`.

---

## 4. Configurar credenciais AWS na sua máquina

O Streamlit roda localmente e precisa de credenciais para acessar Bedrock, DynamoDB e S3.

### Opção A — AWS CLI (recomendado)

Se você já tem o AWS CLI instalado:

```bash
aws configure
```

Preencha:
- **AWS Access Key ID:** sua access key
- **AWS Secret Access Key:** sua secret key
- **Default region name:** us-east-1
- **Default output format:** json

### Opção B — Arquivo .env

Se preferir não usar o CLI, crie o arquivo `.env` na raiz do projeto:

```bash
cp .env.example .env
```

Edite com suas credenciais. **NUNCA commite o .env** (já está no .gitignore).

---

## 5. Verificar permissões IAM

O usuário/role que você está usando precisa das seguintes permissões:

```
bedrock:InvokeModel
bedrock:Converse
dynamodb:GetItem
dynamodb:PutItem
s3:PutObject
s3:GetObject
```

Se estiver usando um usuário admin, já tem tudo. Se for uma role mais restrita, adicione essas permissões.

### Policy JSON (se precisar criar uma custom):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:Converse"
            ],
            "Resource": "arn:aws:bedrock:us-east-1::foundation-model/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem"
            ],
            "Resource": "arn:aws:dynamodb:us-east-1:*:table/dungeonai-game-sessions"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject"
            ],
            "Resource": "arn:aws:s3:::dungeonai-scenes/*"
        }
    ]
}
```

---

## 6. Instalar dependências e rodar

```bash
# Na raiz do projeto
pip install -r requirements.txt

# Rodar o jogo
python -m streamlit run frontend/app.py
```

O Streamlit abre no browser em `http://localhost:8501`.

Clique **Iniciar aventura** → digite uma ação → o agent gera a narrativa + imagem.

---

## Troubleshooting

### "AccessDeniedException" no Bedrock
- Verifique se habilitou os models no passo 1
- Verifique se a região é **us-east-1**
- Verifique se o IAM user tem permissão `bedrock:InvokeModel`

### "ResourceNotFoundException" no DynamoDB
- Verifique se a tabela se chama exatamente `dungeonai-game-sessions`
- Verifique se está na região **us-east-1**

### "NoSuchBucket" no S3
- Verifique se o bucket existe e se o nome no código bate com o nome real
- Se mudou o nome do bucket, atualize em `agent/tools/generate_scene.py`

### Imagem não aparece no Streamlit
- Verifique os logs no terminal — se o Nova Canvas retornar erro, a narrativa aparece mas sem imagem
- O model Titan Image Generator V2 precisa estar com **Access granted** no Bedrock

---

## Estimativa de custo

Para uma sessão de teste (10-20 turnos):

| Serviço | Custo estimado |
|---|---|
| Claude Haiku (narrativa) | ~$0.02 |
| Nova Canvas (imagens) | ~$0.40-0.80 |
| DynamoDB | < $0.01 |
| S3 | < $0.01 |
| **Total por sessão** | **~$0.50-1.00** |

> Dica: se quiser economizar durante o desenvolvimento, comente a chamada do `generate_scene`
> no `dungeon_master.py` e teste só a narrativa primeiro. A imagem é o custo mais alto.
