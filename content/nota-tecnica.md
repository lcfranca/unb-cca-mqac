# Introdução

A pergunta sobre o que torna um ativo comprável atravessa a história das finanças como questão simultaneamente técnica e filosófica. Técnica porque demanda modelos, métricas, procedimentos de avaliação; filosófica porque pressupõe teorias sobre valor, risco, racionalidade dos agentes. Este trabalho situa-se nessa intersecção ao propor análise quantitativa de comprabilidade aplicada à Petrobras S.A. (PETR4), em contexto marcado pela autorização de exploração da Margem Equatorial brasileira — evento catalisador que reorganiza expectativas sobre reservas, fluxos de caixa e perfil de risco da companhia.

A questão central que orienta esta investigação pode ser formulada nos seguintes termos: considerando a expansão para novas fronteiras exploratórias e os riscos ESG/regulatórios associados, a PETR4 representa oportunidade de compra ou armadilha de valor (*value trap*)? O motor quantitativo Q-VAL, desenvolvido ao longo deste trabalho, busca responder a essa pergunta através da identificação de *mispricing* — divergência sistemática entre o custo de capital implícito nos preços de mercado e o custo de capital teórico derivado de modelos de precificação.

A relevância do caso Petrobras transcende o interesse específico no ativo. Trata-se da maior empresa brasileira por capitalização de mercado, componente dominante do índice Ibovespa, e objeto de controvérsias que sintetizam tensões contemporâneas entre rentabilidade, governança corporativa e responsabilidade socioambiental. A análise de comprabilidade da PETR4 constitui, nesse sentido, exercício de aplicação de métodos quantitativos a problema real, onde limitações teóricas dos modelos confrontam-se com a complexidade empírica de empresa sujeita a múltiplas pressões institucionais.

O trabalho estrutura-se em cinco movimentos. Primeiro, estabelece fundamentos teóricos sobre precificação de ativos, revisando o Capital Asset Pricing Model (CAPM) e suas extensões. Segundo, desenvolve arcabouço conceitual para análise fundamentalista quantitativa, articulando métricas de valor, qualidade e risco em sistema de *scoring*. Terceiro, contextualiza historicamente a Petrobras e o cenário atual da Margem Equatorial. Quarto, aplica os modelos aos dados coletados, estimando parâmetros e gerando diagnósticos. Quinto, sintetiza resultados em recomendação de investimento fundamentada.

Os objetivos específicos deste trabalho são:

1. Estimar o custo de capital próprio de PETR4 via CAPM, a partir de dados de retornos históricos;
2. Calcular métricas fundamentalistas organizadas nas dimensões de Valor, Qualidade e Risco;
3. Desenvolver motor de *scoring* Q-VAL integrando as três dimensões em índice sintético;
4. Diagnosticar *mispricing* via comparação entre Implied Cost of Capital e custo teórico;
5. Analisar cenários (base, otimista, pessimista) e sensibilidade do score a variações nas premissas;
6. Emitir recomendação de comprabilidade fundamentada, classificando o ativo como Compra, Neutro ou Venda.

# Fundamentos Teóricos

## Precificação de Ativos: Do CAPM às Extensões Multifatoriais

A teoria moderna de precificação de ativos emerge da revolução quantitativa que transformou as finanças na segunda metade do século XX. O trabalho seminal de @markowitzPortfolioSelection1952 estabeleceu que investidores racionais deveriam avaliar carteiras não apenas por seus retornos esperados, mas também por sua variância — medida de dispersão que captura o risco. A diversificação, nesse enquadramento, opera como mecanismo de redução de risco: combinando ativos imperfeitamente correlacionados, investidores podem alcançar perfis de risco-retorno superiores aos de ativos individuais.

O Capital Asset Pricing Model, desenvolvido independentemente por @sharpeCapitalAssetPrices1964, @lintnerValuationRiskAssets1965 e Mossin [-@mossinEquilibriumCapitalAsset1966], traduziu essas intuições para modelo de equilíbrio geral. Em mercado onde todos os investidores otimizam carteiras segundo critérios média-variância, com expectativas homogêneas e acesso irrestrito a taxa livre de risco, o retorno esperado de qualquer ativo torna-se função linear de seu risco sistemático — o componente de variabilidade que não pode ser eliminado por diversificação. A relação fundamental expressa-se como:

$$E(R_i) = R_f + \beta_i [E(R_m) - R_f]$$

onde $E(R_i)$ denota o retorno esperado do ativo $i$, $R_f$ a taxa livre de risco, $\beta_i$ a sensibilidade do ativo ao mercado (risco sistemático) e $[E(R_m) - R_f]$ o prêmio de risco de mercado. O beta, coeficiente angular da regressão dos retornos do ativo sobre os retornos do mercado, emerge como estatística suficiente para precificação: ativos com beta superior a um amplificam movimentos de mercado e devem oferecer prêmio proporcional; ativos com beta inferior a um atenuam esses movimentos e podem oferecer prêmio menor.

A elegância do CAPM reside em sua parcimônia. Um único fator — o retorno de mercado — explica a seção transversal de retornos esperados. Essa simplicidade, contudo, implica restrições empíricas fortes. @rollCritiqueCAPMTests1977 demonstrou a impossibilidade de testar o CAPM verdadeiro, dado que a carteira de mercado teórica inclui todos os ativos investíveis — problema conhecido como crítica de Roll. Não obstante as dificuldades de testabilidade, décadas de testes revelaram anomalias persistentes: empresas pequenas apresentam retornos superiores ao previsto por seus betas [@benzSmallFirmEffect1981]; ações de valor (*value stocks*), identificadas por múltiplos baixos de preço sobre valor patrimonial, superam sistematicamente ações de crescimento [@rosenbergPersuasiveEvidenceMarket1985]; momentum — tendência de vencedores recentes continuarem vencendo — constitui fenômeno robusto não explicado pelo modelo [@jegadeeshReturnsBuyingWinners1993].

@famaCommonRiskFactors1993 responderam a essas anomalias propondo extensão trifatorial. Além do fator de mercado, incluíram SMB (*Small Minus Big*) — diferença entre retornos de empresas pequenas e grandes — e HML (*High Minus Low*) — diferença entre retornos de ações de valor e crescimento. O modelo de três fatores captura parcela substancial da variação transversal de retornos, embora debates persistam sobre se os fatores adicionais representam risco ou ineficiência de mercado. @famaFiveFactorAssetPricing2015 estenderam posteriormente o modelo para cinco fatores, incorporando lucratividade (RMW, *Robust Minus Weak*) e investimento (CMA, *Conservative Minus Aggressive*).

A Arbitrage Pricing Theory de @rossArbitragePricingAssets1976 oferece enquadramento alternativo. Em vez de derivar fatores de condições de equilíbrio, a APT assume que retornos são gerados por processo linear multifatorial e que arbitragem elimina *mispricing* sistemático. A teoria não especifica quais fatores são relevantes — questão empírica a ser determinada caso a caso. Essa flexibilidade constitui simultaneamente força e fraqueza: permite adaptação a contextos específicos, mas oferece menos orientação sobre quais variáveis incluir.

Para fins deste trabalho, o CAPM tradicional fornece ponto de partida adequado. Sua simplicidade permite estimação robusta com dados disponíveis, enquanto suas limitações são bem compreendidas. O beta estimado via regressão dos retornos de PETR4 sobre retornos do Ibovespa captura a exposição da empresa ao risco sistemático brasileiro. O custo de capital próprio derivado — taxa de retorno que investidores exigem para manter a ação — constitui benchmark contra o qual retornos realizados podem ser comparados.

## Análise Fundamentalista Quantitativa e Sistemas de Scoring

A análise fundamentalista tradicional busca determinar o valor intrínseco de empresas através do exame de demonstrações contábeis, posição competitiva, qualidade da gestão e perspectivas setoriais. @grahamSecurityAnalysis1934 codificaram essa abordagem em tratado que influenciou gerações de investidores, estabelecendo princípios de margem de segurança, diversificação e disciplina analítica. A tradição fundamentalista assume que preços de mercado podem divergir temporariamente do valor intrínseco, mas convergem no longo prazo — premissa que justifica o trabalho de análise.

A quantificação dessa tradição implica traduzir julgamentos qualitativos para métricas comparáveis. O movimento ganhou impulso com a disponibilização de bases de dados computadorizadas e poder de processamento para analisar grandes amostras de empresas. @piotroskiValueInvestingUse2000 demonstrou que estratégia baseada em nove indicadores contábeis binários — o *F-Score* — gerava retornos anormais significativos entre ações de valor. @greenHandZhang2017 estenderam a abordagem identificando características que fornecem informação independente sobre retornos, confirmando a utilidade de sinais fundamentalistas em contextos diversos.

Um sistema de *scoring* fundamentalista articula múltiplas dimensões de avaliação em índice sintético. A construção desse sistema envolve três decisões: quais métricas incluir, como normalizá-las para escala comum, e como ponderá-las no índice final. O motor Q-VAL proposto neste trabalho organiza métricas em três dimensões — Valor, Qualidade e Risco — buscando equilibrar sinais de preço, desempenho operacional e perfil de risco financeiro.

A dimensão de Valor captura a relação entre preço de mercado e fundamentos contábeis. Métricas como Preço/Lucro (P/L), Preço/Valor Patrimonial (P/VP), EV/EBITDA e *Dividend Yield* indicam quanto investidores pagam por unidade de lucro, patrimônio, geração de caixa ou distribuição de dividendos. Valores baixos sugerem desconto em relação a pares ou médias históricas; valores elevados indicam prêmio. A interpretação não é mecânica: múltiplo baixo pode refletir oportunidade de compra ou deterioração estrutural dos fundamentos. A combinação com outras dimensões ajuda a distinguir entre as possibilidades.

A dimensão de Qualidade avalia a eficiência operacional e a sustentabilidade dos resultados. Retorno sobre patrimônio líquido (ROE), retorno sobre ativos (ROA), margens operacionais e crescimento de receitas indicam a capacidade da empresa de gerar valor para acionistas. Qualidade elevada sugere vantagens competitivas duráveis — o que @buffettEssaysWarrenBuffett1997 denominou *moat* econômico. Empresas de alta qualidade negociando a múltiplos baixos constituem, nessa perspectiva, as oportunidades mais atrativas.

A dimensão de Risco incorpora indicadores de alavancagem, liquidez e volatilidade. Dívida sobre patrimônio, cobertura de juros, liquidez corrente e beta medem diferentes facetas da exposição a eventos adversos. A alavancagem amplifica retornos em cenários favoráveis e perdas em cenários desfavoráveis; a liquidez determina a capacidade de honrar compromissos de curto prazo; o beta captura a sensibilidade a oscilações de mercado. A combinação dessas métricas permite calibrar expectativas de retorno ao perfil de risco.

## O Economic Value Spread como Métrica de Criação de Valor

O Economic Value Spread (EVS) constitui métrica desenvolvida para capturar a criação de valor em termos relativos ao custo de capital. A intuição é direta: empresa cria valor quando obtém retorno sobre capital investido superior ao custo desse capital; destrói valor quando ocorre o inverso. O EVS quantifica essa diferença, permitindo comparações entre empresas e ao longo do tempo.

Formalmente, o EVS pode ser definido como:

$$EVS = ROIC - WACC$$

onde ROIC denota o retorno sobre capital investido e WACC o custo médio ponderado de capital. Valor positivo indica criação de valor; valor negativo indica destruição. A magnitude do EVS reflete a intensidade do processo: empresa com EVS de 5% cria valor de forma mais substancial que empresa com EVS de 1%, *ceteris paribus*.

O EVS relaciona-se com o conceito de Valor Econômico Agregado (EVA) desenvolvido por @stewartQuestValueGuide1991. Enquanto o EVA expressa criação de valor em termos monetários absolutos — multiplicando o spread pelo capital investido —, o EVS expressa em termos percentuais, facilitando comparações. Ambas as métricas compartilham a virtude de incorporar explicitamente o custo de oportunidade do capital, dimensão frequentemente negligenciada em análises baseadas apenas em lucro contábil.

Para empresas do setor de óleo e gás, o EVS assume relevância particular. Trata-se de indústria intensiva em capital, com ciclos de investimento longos e exposição significativa a oscilações de preços de commodities. A capacidade de gerar retorno consistentemente superior ao custo de capital — de manter EVS positivo através de ciclos — distingue operadores eficientes de empresas que destroem valor de acionistas enquanto expandem reservas e produção.

# Contextualização: Petrobras e a Margem Equatorial

## Trajetória Histórica e Institucional

A Petróleo Brasileiro S.A. — Petrobras — foi constituída em 1953 como instrumento da política desenvolvimentista que marcou o período Vargas. A criação da empresa estatal respondeu a demandas nacionalistas por controle dos recursos petrolíferos, sintetizadas na campanha "O Petróleo é Nosso" que mobilizou segmentos diversos da sociedade brasileira. O monopólio estatal sobre exploração, produção e refino, estabelecido pela Lei 2.004/1953, configurou modelo que prevaleceria por mais de quatro décadas.

A quebra parcial do monopólio em 1997, durante o governo Fernando Henrique Cardoso, inaugurou nova fase. A Emenda Constitucional nº 9/1995 e a Lei do Petróleo (9.478/1997) permitiram a entrada de empresas privadas no setor, embora a Petrobras mantivesse posição dominante. A abertura de capital, com listagem simultânea na B3 e NYSE, introduziu pressões de governança corporativa e transparência típicas de companhias abertas. A empresa passou a operar sob dupla lógica: instrumento de política energética nacional e maximizadora de valor para acionistas.

A descoberta do pré-sal em 2006 representou inflexão histórica. As reservas identificadas na camada de rochas carbonáticas sob espessa camada de sal, em águas ultraprofundas da Bacia de Santos, posicionaram o Brasil entre as principais fronteiras petrolíferas globais. O desenvolvimento do pré-sal exigiu investimentos massivos em tecnologia de perfuração e produção em condições extremas — capacidade que a Petrobras desenvolveu tornando-se referência mundial em águas profundas.

O período subsequente foi marcado por escândalo de corrupção de proporções inéditas. A Operação Lava Jato, deflagrada em 2014, revelou esquema de pagamentos ilícitos envolvendo contratos da Petrobras, partidos políticos e empreiteiras. As consequências foram severas: baixas contábeis bilionárias, rebaixamento de rating de crédito, queda abrupta do valor de mercado, e crise de governança que culminou em renovação completa da alta administração. A recuperação, iniciada a partir de 2016, envolveu desinvestimentos, redução de alavancagem e foco em ativos de maior rentabilidade — notadamente o pré-sal.

## O Cenário Atual: Margem Equatorial e Transição Energética

A Margem Equatorial brasileira compreende as bacias sedimentares da costa norte do país, estendendo-se do Amapá ao Rio Grande do Norte. Trata-se de fronteira exploratória praticamente inexplorada, com potencial estimado entre 10 e 30 bilhões de barris de petróleo — volume que poderia duplicar as reservas provadas brasileiras. A região apresenta características geológicas análogas a províncias produtoras da costa oeste africana, onde descobertas significativas foram realizadas nas últimas décadas.

A autorização para exploração da Margem Equatorial, concedida pelo IBAMA em 2024-2025, reacendeu debates sobre a estratégia de longo prazo da Petrobras. De um lado, a exploração representa oportunidade de expansão de reservas em momento em que campos maduros declinam e o pré-sal, embora produtivo, apresenta horizonte finito. De outro, implica investimentos vultosos — estimados entre US$ 50 e 100 bilhões — com retorno incerto e prazo de maturação superior a uma década.

O contexto de transição energética adiciona camada de complexidade à decisão. O Acordo de Paris e os compromissos subsequentes de neutralidade de carbono pressionam empresas petrolíferas a reorientar portfólios para fontes renováveis. Investidores institucionais, especialmente fundos de pensão europeus e gestores com mandatos ESG, questionam a racionalidade de investimentos em novas fronteiras fósseis. A Petrobras enfrenta, nesse cenário, tensão entre maximização de valor de curto prazo via exploração de reservas e posicionamento estratégico para economia descarbonizada.

Os riscos regulatórios e ambientais da Margem Equatorial são substanciais. A região abriga ecossistemas sensíveis, incluindo manguezais, recifes de coral e áreas de reprodução de espécies marinhas. O licenciamento ambiental tem sido objeto de contestação judicial e mobilização de organizações ambientalistas. Vazamentos ou acidentes em área de difícil acesso teriam consequências potencialmente graves, com repercussões sobre a reputação da empresa e sua licença social para operar.

## Implicações para Valuation

A avaliação da PETR4 no contexto descrito envolve ponderação de cenários com probabilidades e payoffs distintos. No cenário otimista, a exploração da Margem Equatorial confirma potencial geológico, custos de desenvolvimento permanecem controlados, e preços de petróleo sustentam-se em patamares remuneradores. Os fluxos de caixa incrementais justificam o investimento e o valor da empresa aumenta significativamente. No cenário pessimista, reservas mostram-se menores que o esperado, custos escalam além das projeções, preços de petróleo colapsam com aceleração da transição energética, e pressões ESG restringem acesso a capital. Os investimentos tornam-se *stranded assets* e o valor da empresa deteriora-se.

O mercado, ao precificar a PETR4, pondera implicitamente esses cenários. A pergunta relevante para o investidor é se essa ponderação está correta — se o preço corrente reflete adequadamente o valor esperado da empresa considerando probabilidades e magnitudes dos diferentes cenários. A análise de *mispricing* via comparação entre custo de capital implícito e custo de capital teórico (CAPM) oferece uma abordagem para essa questão.

# Metodologia

## Capital Asset Pricing Model (CAPM)

O CAPM fornece o arcabouço teórico para estimação do custo de capital próprio. A relação fundamental, derivada de condições de equilíbrio em mercado de capitais, estabelece que o retorno esperado de qualquer ativo é função linear de seu risco sistemático:

$$E(R_i) = R_f + \beta_i [E(R_m) - R_f]$$

onde $E(R_i)$ representa o retorno esperado do ativo $i$, $R_f$ a taxa livre de risco, $\beta_i$ o coeficiente de sensibilidade ao mercado (beta), e $[E(R_m) - R_f]$ o prêmio de risco de mercado. O beta captura a contribuição marginal do ativo para o risco de carteira diversificada: ativos com beta elevado amplificam movimentos de mercado e exigem prêmio correspondente; ativos com beta baixo atenuam esses movimentos e podem ser mantidos com prêmio menor.

## Estratégia Empírica

### Estimação do Beta via Regressão Linear

O beta é estimado através de regressão dos retornos em excesso do ativo sobre os retornos em excesso do mercado:

$$R_{i,t} - R_{f,t} = \alpha_i + \beta_i (R_{m,t} - R_{f,t}) + \varepsilon_{i,t}$$

onde $R_{i,t}$ denota o retorno do ativo no período $t$, $R_{f,t}$ a taxa livre de risco, $R_{m,t}$ o retorno do mercado, $\alpha_i$ o intercepto (alfa de Jensen), $\beta_i$ o coeficiente de interesse, e $\varepsilon_{i,t}$ o termo de erro. O alfa captura o retorno anormal — componente de retorno não explicado pela exposição ao mercado. Alfa positivo sugere desempenho superior ao previsto pelo CAPM; alfa negativo indica desempenho inferior.

A Figura \ref{fig:regressao_beta} apresenta o resultado da regressão aplicada aos dados de PETR4 e Ibovespa. A inclinação da reta de regressão corresponde ao beta estimado; a dispersão dos pontos em torno da reta reflete o risco idiossincrático — componente de variabilidade específico da empresa, não correlacionado com o mercado. A literatura documenta tendência de regressão à média dos betas ao longo do tempo [@blumeBetaRegressionMean1971], sugerindo que ajustes como $\beta_{adj} = 0.67\beta + 0.33$ podem melhorar previsões futuras; neste trabalho, optou-se pelo beta bruto para preservar transparência metodológica.

\begin{figure}[H]
\centering
\includegraphics[width=0.70\textwidth]{data/outputs/figures/regressao_beta.pdf}
\caption{Estimação do Beta via Regressão Linear}
\label{fig:regressao_beta}
\end{figure}

### Linha de Mercado de Títulos (SML)

A Linha de Mercado de Títulos representa graficamente a relação de equilíbrio do CAPM. No eixo horizontal, o beta mede o risco sistemático; no eixo vertical, o retorno esperado. A SML intercepta o eixo vertical na taxa livre de risco (beta zero) e passa pelo ponto de mercado (beta um, retorno de mercado). Ativos corretamente precificados situam-se sobre a linha; ativos acima da linha oferecem retorno superior ao requerido (subprecificados); ativos abaixo da linha oferecem retorno inferior (sobreprecificados).

A Figura \ref{fig:sml_capm} posiciona PETR4 em relação à SML estimada. A distância vertical entre o ponto da empresa e a linha indica o *mispricing* — divergência entre retorno realizado e retorno previsto pelo modelo. Distância positiva sugere oportunidade de compra; distância negativa sugere cautela ou venda.

\begin{figure}[H]
\centering
\includegraphics[width=0.70\textwidth]{data/outputs/figures/sml_capm.pdf}
\caption{Linha de Mercado de Títulos (SML)}
\label{fig:sml_capm}
\end{figure}

### Análise da Distribuição de Retornos

A análise da distribuição de retornos complementa a estimação pontual de parâmetros. A Figura \ref{fig:distribuicao} apresenta histogramas dos retornos diários de PETR4 e do Ibovespa, permitindo avaliar assimetria, curtose e presença de valores extremos. Retornos de ativos financeiros frequentemente exibem caudas pesadas — probabilidade de eventos extremos superior à prevista pela distribuição normal —, característica relevante para gestão de risco.

\begin{figure}[H]
\centering
\includegraphics[width=0.85\textwidth]{data/outputs/figures/distribuicao_retornos.pdf}
\caption{Distribuição dos Retornos}
\label{fig:distribuicao}
\end{figure}

## Fontes de Dados e Tratamento

Os dados utilizados neste trabalho foram coletados de três fontes complementares. Os preços históricos e dados fundamentalistas de PETR4 foram obtidos via API Brapi, que disponibiliza informações do mercado brasileiro em formato estruturado. O índice Ibovespa, utilizado como *proxy* para a carteira de mercado, foi coletado via Yahoo Finance através da biblioteca *yfinance*. A taxa SELIC, utilizada como *proxy* para a taxa livre de risco, foi obtida diretamente do Banco Central do Brasil através do Sistema Gerenciador de Séries Temporais (SGS).

O período de análise estende-se de janeiro de 2016 a novembro de 2025, compreendendo aproximadamente 2.460 observações diárias. A escolha do período inicial justifica-se por capturar o ponto de inflexão na trajetória da empresa — o momento de maior depreciação das ações durante a crise de 2015-2016 — permitindo observação de ciclo completo de recuperação. Os retornos foram calculados em base logarítmica, $r_t = \ln(P_t/P_{t-1})$, e os retornos em excesso computados pela subtração da taxa SELIC diária equivalente.

# Resultados

## Estatísticas Descritivas

A Tabela \ref{tab:estatisticas_descritivas} apresenta estatísticas descritivas dos retornos analisados. O retorno médio diário de PETR4, a volatilidade (desvio-padrão dos retornos), e medidas de assimetria e curtose permitem caracterizar o comportamento da série ao longo do período.

\input{data/outputs/tables/estatisticas_descritivas.tex}

## Estimação do CAPM e Custo de Capital

Os resultados da estimação do CAPM são apresentados na Tabela \ref{tab:resultados_capm}. O beta estimado indica a sensibilidade de PETR4 aos movimentos do mercado; o alfa indica retorno anormal acumulado no período; o $R^2$ indica a proporção da variância de retornos explicada pelo fator de mercado.

\input{data/outputs/tables/resultados_capm.tex}

### Matriz de Correlação

A Figura \ref{fig:correlacao} apresenta a correlação entre os retornos de PETR4 e do Ibovespa. Correlação elevada indica que movimentos de mercado explicam parcela substancial da variabilidade do ativo; correlação baixa sugere presença significativa de fatores idiossincráticos.

\begin{figure}[H]
\centering
\includegraphics[width=0.60\textwidth]{data/outputs/figures/correlacao.pdf}
\caption{Matriz de Correlação}
\label{fig:correlacao}
\end{figure}

## Análise de Risco e Limitações

A aplicação do CAPM a mercados emergentes como o brasileiro envolve limitações conhecidas. A volatilidade superior à de mercados desenvolvidos, a concentração setorial do índice de referência, e a presença de controles de capital introduzem ruídos na estimação. O beta estimado reflete exposição ao risco sistemático doméstico, mas não captura integralmente riscos específicos de empresa estatal sujeita a interferências políticas.

Adicionalmente, o período amostral inclui eventos de magnitude excepcional — a crise política de 2015-2016, a pandemia de COVID-19 em 2020, e oscilações abruptas de preços de petróleo —, que podem distorcer estimativas. A interpretação dos resultados deve considerar essas ressalvas, tratando as estimativas pontuais como aproximações sujeitas a incerteza substancial.

## Métricas Fundamentalistas e Score Q-VAL

A Tabela \ref{tab:metricas_fundamentalistas} apresenta as métricas fundamentalistas calculadas para PETR4, organizadas nas três dimensões do motor Q-VAL: Valor, Qualidade e Risco. Cada métrica é acompanhada de seu Z-Score normalizado em relação aos benchmarks setoriais.

\input{data/outputs/tables/metricas_fundamentalistas.tex}

A Tabela \ref{tab:score_comprabilidade} sintetiza o cálculo do score final de comprabilidade, mostrando as contribuições de cada dimensão e a recomendação derivada.

\input{data/outputs/tables/score_comprabilidade.tex}

A Figura \ref{fig:radar_score} visualiza as três dimensões do score Q-VAL em formato radar, permitindo identificar rapidamente forças e fraquezas do ativo em cada dimensão.

\begin{figure}[H]
\centering
\includegraphics[width=0.70\textwidth]{data/outputs/figures/radar_score.pdf}
\caption{Radar do Score Q-VAL}
\label{fig:radar_score}
\end{figure}

## Análise de Valuation e Mispricing

A Tabela \ref{tab:valuation_multiplos} apresenta os múltiplos de valuation de PETR4 comparados com médias históricas e setoriais. A comparação permite identificar prêmios ou descontos em relação a benchmarks relevantes.

\input{data/outputs/tables/valuation_multiplos.tex}

A Tabela \ref{tab:diagnostico_mispricing} apresenta o diagnóstico de mispricing via comparação entre o Custo de Capital Implícito (ICC) e o custo de capital teórico derivado do CAPM. A metodologia de ICC, fundamentada em @gebhardtTowardImpliedCost2001, extrai o custo de capital implícito nos preços de mercado, permitindo diagnóstico de sobre ou subprecificação. A aplicação a mercados emergentes como o Brasil requer cautela adicional, dado que o CAPM pode capturar inadequadamente riscos específicos desses mercados [@harveyPredictableRiskReturns1995].

\input{data/outputs/tables/diagnostico_mispricing.tex}

A Figura \ref{fig:icc_vs_capm} visualiza a comparação entre ICC e Ke do CAPM, evidenciando a magnitude e direção do spread.

\begin{figure}[H]
\centering
\includegraphics[width=0.70\textwidth]{data/outputs/figures/icc_vs_capm.pdf}
\caption{Custo de Capital Implícito vs. CAPM}
\label{fig:icc_vs_capm}
\end{figure}

## Análise de Cenários

A Tabela \ref{tab:cenarios_valuation} apresenta os resultados da análise de cenários, considerando premissas base, otimista e pessimista para as principais variáveis que afetam a valuation de PETR4.

\input{data/outputs/tables/cenarios_valuation.tex}

A Figura \ref{fig:sensibilidade_score} apresenta a análise de sensibilidade do score Q-VAL às variações nas premissas, identificando as variáveis de maior impacto.

\begin{figure}[H]
\centering
\includegraphics[width=0.85\textwidth]{data/outputs/figures/sensibilidade_score.pdf}
\caption{Análise de Sensibilidade do Score Q-VAL}
\label{fig:sensibilidade_score}
\end{figure}

# Discussão

## Interpretação do Beta e Custo de Capital

O beta estimado de 1,40 para PETR4 indica sensibilidade amplificada aos movimentos do Ibovespa. A cada variação de 1% no índice de mercado, espera-se variação de aproximadamente 1,4% no retorno da ação — característica consistente com o perfil de empresa cíclica, fortemente exposta a oscilações de preços de commodities e ao sentimento macroeconômico brasileiro. O $R^2$ de 51,67% revela que pouco mais da metade da variabilidade dos retornos de PETR4 é explicada pelo fator de mercado; os 48% restantes decorrem de fatores idiossincráticos — riscos específicos da empresa, do setor de petróleo, e da governança de estatal.

A magnitude do beta reflete a natureza da Petrobras como ativo de alta volatilidade no contexto brasileiro. A volatilidade anualizada de 45,78% — quase o dobro dos 23,50% do Ibovespa — posiciona PETR4 entre os ativos mais arriscados do índice. Essa volatilidade elevada resulta da combinação de exposição a preços internacionais de petróleo (denominados em dólar), risco cambial, risco regulatório, e incertezas sobre política de preços de combustíveis e dividendos.

O custo de capital próprio de 16,60%, derivado do CAPM com prêmio de risco de mercado de 5,5%, estabelece o hurdle rate implícito para criação de valor. Qualquer investimento da Petrobras deve gerar retorno esperado superior a esse patamar para ser considerado acretivo ao acionista. A taxa elevada reflete o perfil de risco descrito: investidores exigem prêmio substancial para manter exposição a ativo tão volátil e sujeito a interferências.

O alfa de Jensen positivo (+0,26% ao ano) sugere que, no período analisado, PETR4 gerou retorno marginalmente superior ao previsto pelo CAPM — evidência tênue de *mispricing* favorável ou de exposição a fatores de risco não capturados pelo modelo unifatorial. A magnitude modesta do alfa e sua sensibilidade ao período amostral recomendam cautela na interpretação: trata-se de indicador histórico, não de previsão de desempenho futuro.

## Economic Value Spread e Criação de Valor

O Economic Value Spread de -1,51% (ROACE de 15,09% versus Ke de 16,60%) indica que, no período mais recente, a Petrobras opera em regime de destruição marginal de valor econômico. O retorno sobre capital empregado, embora positivo em termos absolutos, fica aquém do custo de oportunidade do capital — investidores poderiam, em teoria, obter retorno superior em ativos de risco equivalente.

A interpretação do EVS negativo demanda contextualização. Primeiro, a métrica captura momento específico do ciclo de negócios; empresas de óleo e gás oscilam naturalmente entre criação e destruição de valor conforme preços de commodities e estágio de investimentos. Segundo, o ROACE calculado reflete resultados de ativos maduros enquanto o capital empregado inclui investimentos em desenvolvimento cujos retornos ainda não se materializaram. Terceiro, a política de dividendos agressiva da Petrobras — *payout* superior a 85% — prioriza distribuição sobre reinvestimento, decisão racional se oportunidades de investimento não superam o custo de capital.

O Z-Score negativo do EVS (-0,30) contribui para pressionar o componente de Qualidade do score Q-VAL. Contudo, a magnitude relativamente baixa sugere que a destruição de valor é marginal, não estrutural. A empresa opera próximo ao limiar de criação de valor — condição que pode reverter com melhoria de margens, redução de custos, ou elevação de preços de petróleo.

## Score de Comprabilidade no Contexto Atual

O score Q-VAL de 53,4 posiciona PETR4 na faixa Neutra do espectro de comprabilidade. A decomposição por dimensão revela perfil assimétrico: forte em Valor (Z = +1,31), moderado em Qualidade (Z = +0,54), e fraco em Risco (Z = -0,90). A recomendação Neutra emerge da ponderação desses componentes, onde a atratividade de valuation é parcialmente compensada pelo perfil de risco elevado.

A dimensão de Valor apresenta Z-Scores consistentemente positivos. O Earnings Yield de 18,66% (Z = +1,73), o EV/EBITDA de 1,97x (Z = +1,69), e o P/VP de 0,99x (Z = +0,52) indicam que a empresa negocia com desconto significativo em relação a benchmarks setoriais. Em múltiplos históricos, PETR4 negocia com desconto de 17,5% no P/L e 48,2% no EV/EBITDA em relação às médias dos últimos cinco anos. O Dividend Yield de 15,89% representa prêmio de 32% sobre a média histórica, sinalizando atratividade para investidores orientados a renda.

A dimensão de Qualidade apresenta resultados mistos. O ROACE de 15,09% (Z = +1,27) indica rentabilidade sobre capital empregado superior à média setorial — mérito operacional relevante em indústria intensiva em capital. A Margem EBITDA de 43,79% (Z = +0,88) confirma eficiência operacional robusta. Contudo, o ROE de 8,75% (Z = -0,54) e o EVS negativo comprometem a avaliação agregada. A qualidade operacional é parcialmente dissipada pelo custo de capital elevado e pela estrutura de capital.

A dimensão de Risco apresenta Z-Scores predominantemente negativos. O beta de 1,40 (Z = -1,33) e a volatilidade de 45,78% (Z = -1,08) indicam perfil de risco substancialmente superior à média do setor. Esses indicadores refletem não apenas a natureza cíclica do negócio de petróleo, mas também riscos específicos de governança, regulação e política de preços. O Dividend Yield elevado oferece compensação parcial na forma de retorno defensivo, mas não neutraliza o impacto negativo do risco sistemático.

## PETR4: Oportunidade ou Value Trap?

A pergunta central deste trabalho — se PETR4 representa oportunidade de compra ou armadilha de valor — admite resposta nuançada à luz dos resultados. Os indicadores de valor são inequivocamente atrativos: múltiplos baixos, dividend yield elevado, desconto substancial em relação a médias históricas e setoriais. Esses sinais tipicamente caracterizam oportunidades de valor. Contudo, a persistência de múltiplos baixos ao longo de período extenso levanta questão sobre se o mercado precifica corretamente riscos não capturados pelos múltiplos tradicionais.

A análise de mispricing via ICC oferece perspectiva adicional. O spread de +40 basis points entre ICC (17,00%) e Ke do CAPM (16,60%) situa-se dentro da faixa de precificação justa (±50 bps). O mercado, ao precificar PETR4, exige retorno implícito marginalmente superior ao previsto pelo CAPM — possível indicação de prêmio por riscos específicos não capturados pelo modelo unifatorial. A classificação resultante — Precificação Justa — alinha-se com a recomendação Neutra do score Q-VAL.

O modelo de Gordon sugere valor justo de R\$ 30,44, marginalmente inferior ao preço de mercado de R\$ 31,79 (downside de -4,3%). A estimativa reflete premissas conservadoras: taxa de crescimento de dividendos nula, consistente com *payout* elevado e ROE modesto. Em cenário de crescimento positivo — plausível se investimentos na Margem Equatorial se mostrarem rentáveis — o valor justo aumentaria significativamente.

A análise de cenários revela faixa ampla de possibilidades. No cenário otimista (Brent US\$ 90, Margem Equatorial produzindo), o score Q-VAL sobe para 62,8 (Compra) e o valor justo atinge R\$ 44,10 (upside de +38,7%). No cenário pessimista (Brent US\$ 50, bloqueio da Margem Equatorial), o score cai para 43,0 (Venda) e o valor justo recua para R\$ 23,72 (downside de -25,4%). A amplitude de quase 20 pontos no score e de R\$ 20 no valor justo ilustra a sensibilidade da tese de investimento às premissas sobre variáveis exógenas.

**Conclusão sobre comprabilidade**: PETR4 não configura, na análise presente, nem oportunidade clara de compra nem armadilha de valor evidente. A classificação Neutra reflete equilíbrio entre atratividade de valuation e perfil de risco elevado. Para investidores com horizonte de longo prazo e tolerância a volatilidade, os múltiplos baixos e o dividend yield elevado oferecem combinação atrativa. Para investidores avessos a risco ou com horizontes curtos, a volatilidade de 45% e a exposição a riscos político-regulatórios representam obstáculos significativos.

A Margem Equatorial constitui variável-chave para a evolução da tese. Sucesso exploratório e desenvolvimento rentável deslocariam o score para território de Compra; bloqueio regulatório ou decepção geológica pressionariam para Venda. A recomendação Neutra reflete, em última instância, a incerteza genuína sobre o desfecho dessa fronteira exploratória.

## Limitações do Modelo

O motor Q-VAL, como qualquer modelo de análise, apresenta limitações que devem ser consideradas na interpretação dos resultados.

**Simplificação do CAPM**: O modelo unifatorial captura apenas risco sistemático de mercado. Fatores adicionais — tamanho, valor, momentum, qualidade — podem explicar parcela significativa dos retornos não atribuída ao beta. A omissão desses fatores potencialmente distorce a estimativa de custo de capital e, consequentemente, o diagnóstico de mispricing.

**Normalização setorial**: Os Z-Scores utilizam benchmarks setoriais que podem não refletir adequadamente o universo comparável de PETR4. Empresas integradas de óleo e gás variam significativamente em escala, mix de ativos e exposição geográfica. A Petrobras, como estatal de mercado emergente com concentração em águas profundas, pode não ser diretamente comparável a majors globais privadas.

**Linearidade das ponderações**: O score Q-VAL assume combinação linear das dimensões de Valor, Qualidade e Risco. Interações não-lineares — onde, por exemplo, risco elevado deveria penalizar mais fortemente ativos de qualidade baixa — não são capturadas. A especificação linear representa compromisso entre simplicidade e precisão.

**Estacionariedade das relações**: Os parâmetros estimados (beta, médias setoriais, pesos) assumem estabilidade ao longo do tempo. Em realidade, essas relações podem variar com mudanças estruturais no mercado, no setor ou na empresa. A crise de 2015-2016 e a recuperação subsequente ilustram como parâmetros podem deslocar-se significativamente.

**Dados fundamentalistas defasados**: As métricas contábeis refletem resultados passados, enquanto preços de mercado incorporam expectativas futuras. A defasagem temporal pode gerar sinais espúrios quando fundamentos estão em trajetória de mudança. O período de *lag* entre divulgação de resultados e reação de mercado adiciona ruído à análise.

**Ausência de análise qualitativa**: O modelo quantifica métricas observáveis mas não captura dimensões qualitativas relevantes — qualidade da gestão, posicionamento estratégico, cultura organizacional, relacionamento com stakeholders. Esses fatores, embora difíceis de mensurar, podem ter impacto material sobre criação de valor de longo prazo.

Reconhecidas essas limitações, o motor Q-VAL cumpre papel de sistematização e disciplina analítica. A transparência metodológica permite que usuários ajustem pesos, revisem benchmarks ou incorporem julgamentos qualitativos conforme suas convicções. O score de 53,4 e a recomendação Neutra devem ser interpretados não como veredicto definitivo, mas como ponto de partida informado para tomada de decisão de investimento.

# Conclusão

Este trabalho propôs-se a investigar a comprabilidade da Petrobras S.A. (PETR4) no contexto da autorização de exploração da Margem Equatorial brasileira, mobilizando ferramentas quantitativas para responder à questão: oportunidade de compra ou armadilha de valor? A resposta, como frequentemente ocorre em problemas de investimento genuínos, mostrou-se mais nuançada do que dicotomias simples permitem capturar.

O motor Q-VAL, desenvolvido como instrumento de análise multidimensional, integrou métricas de Valor, Qualidade e Risco em sistema de *scoring* fundamentado teoricamente e calibrado empiricamente. A estimação do CAPM revelou beta de 1,40 — sensibilidade amplificada ao mercado brasileiro consistente com perfil de empresa cíclica, estatal, exposta a commodities e risco cambial. O custo de capital próprio resultante, de 16,60%, estabeleceu o patamar mínimo de retorno exigido por investidores racionais para manter exposição ao ativo.

A análise fundamentalista quantificou três dimensões de avaliação. Na dimensão de Valor, os múltiplos de PETR4 indicam desconto substancial: P/L de 5,36x versus média setorial de 8,00x; EV/EBITDA de 1,97x versus 4,50x; Dividend Yield de 15,89% versus 8,00%. Esses indicadores, isoladamente, sinalizariam oportunidade de compra. Contudo, a dimensão de Risco revelou volatilidade anualizada de 45,78% e beta elevado — perfil que justifica, ao menos parcialmente, o desconto observado. A dimensão de Qualidade apresentou resultados mistos: eficiência operacional robusta (Margem EBITDA de 43,79%, ROACE de 15,09%) coexistindo com Economic Value Spread negativo (-1,51%), indicador de destruição marginal de valor quando comparado ao custo de capital.

O score Q-VAL de 53,4 — na faixa Neutra do espectro de 0 a 100 — sintetizou essas tensões. A recomendação Neutra não significa indiferença; significa que, dados os parâmetros estimados e as incertezas prevalentes, nem a compra nem a venda se impõem como estratégia claramente dominante. O diagnóstico de *mispricing* via Implied Cost of Capital corroborou essa conclusão: o spread de +40 basis points entre ICC (17,00%) e Ke do CAPM (16,60%) situa-se dentro da faixa de precificação justa, indicando que o mercado, em média, avalia corretamente os riscos e retornos esperados do ativo.

A análise de cenários iluminou a dependência da tese de investimento a variáveis exógenas. No cenário otimista — Margem Equatorial produzindo, Brent a US\$ 90/barril —, o score Q-VAL ascende a 62,8 (Compra) e o valor justo atinge R\$ 44,10 (upside de 38,7%). No cenário pessimista — bloqueio regulatório, Brent a US\$ 50/barril —, o score recua para 43,0 (Venda) e o valor justo cai para R\$ 23,72 (downside de 25,4%). A amplitude de quase 20 pontos no score e de R\$ 20 no valor justo evidencia que a decisão de investimento em PETR4 é, em última instância, aposta sobre o desfecho de incertezas genuínas — geológicas, regulatórias, macroeconômicas — que transcendem a capacidade preditiva de modelos quantitativos.

A Margem Equatorial emerge, nesse contexto, como catalisador central. Sucesso exploratório transformaria PETR4 em caso exemplar de *value investing* — ativo subprecificado cujo valor intrínseco se revelou superior às expectativas de mercado. Fracasso — seja por decepção geológica, bloqueio ambiental ou obsolescência acelerada de ativos fósseis — configuraria a armadilha de valor que investidores prudentes buscam evitar. A classificação Neutra reflete, honestamente, a impossibilidade de prever com confiança qual desses desfechos prevalecerá.

Do ponto de vista metodológico, o trabalho demonstrou a viabilidade de construir motor de *scoring* quantitativo integrado, capaz de articular teoria de precificação de ativos, análise fundamentalista e diagnóstico de *mispricing* em arcabouço coerente. O motor Q-VAL não pretende substituir julgamento humano; pretende discipliná-lo, sistematizando informações disponíveis e explicitando premissas subjacentes a recomendações de investimento. A transparência do modelo — com pesos, benchmarks e fórmulas documentados — permite que usuários ajustem parâmetros conforme suas convicções e tolerância a risco.

As limitações identificadas — simplificação do CAPM, linearidade das ponderações, estacionariedade presumida das relações — apontam direções para aprofundamento. Extensões naturais incluiriam incorporação de fatores adicionais (tamanho, momentum, qualidade), especificação não-linear do score, e atualização dinâmica de parâmetros. A aplicação a outros ativos e setores permitiria calibração mais robusta dos benchmarks setoriais e validação *out-of-sample* do modelo.

Em síntese, a pergunta que motivou este trabalho — se PETR4 representa oportunidade ou armadilha — recebe resposta condicional: **depende**. Depende da evolução de preços de petróleo, do sucesso da Margem Equatorial, da trajetória regulatória, do ritmo da transição energética. Para investidores com horizonte longo, tolerância a volatilidade e convicção no cenário otimista, os múltiplos atuais oferecem entrada atrativa. Para investidores avessos a risco ou céticos quanto ao futuro de combustíveis fósseis, a prudência recomenda posicionamento neutro ou alternativas de menor volatilidade. O motor Q-VAL, ao quantificar essas considerações, cumpre seu papel: não decide pelo investidor, mas informa sua decisão.

# Referências {.unnumbered}

::: {#refs}
:::
