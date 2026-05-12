---
source_file: "LimitOrderBook.pdf"
total_pages: 14
---



<!-- PAGE 1 -->

High-frequency trading in a limit order book
Marco Avellaneda & Sasha Stoikov
October 5, 2006
Abstract
We study a stock dealer’s strategy for submitting bid and ask quotes in a
limit order book. The agent faces an inventory risk due to the diﬀusive nature of
the stock’s mid-price and a transactions risk due to a Poisson arrival of market
buy and sell orders. After setting up the agent’s problem in a maximal expected
utility framework, we derive the solution in a two step procedure. First, the
dealer computes a personal indiﬀerence valuation for the stock, given his current
inventory. Second, he calibrates his bid and ask quotes to the market’s limit
order book. We compare this ”inventory-based” strategy to a ”naive” strategy
that is symmetric around the mid-price, by simulating stock price paths and
displaying the P&L proﬁles of both strategies. We ﬁnd that our strategy yields
P&L proﬁles and ﬁnal inventories that have signiﬁcantly less variance than the
benchmark strategy.
1
Introduction
The role of a dealer in securities markets is to provide liquidity on the exchange by
quoting bid and ask prices at which he is willing to buy and sell a speciﬁc quan-
tity of assets. Traditionally, this role has been ﬁlled by market-maker or specialist
ﬁrms. In recent years, with the growth of electronic exchanges such as Nasdaq’s Inet,
anyone willing to submit limit orders in the system can eﬀectively play the role of a
dealer. Indeed, the availability of high frequency data on the limit order book (see
www.inetats.com) ensures a fair playing ﬁeld where various agents can post limit
orders at the prices they choose. In this paper, we study the optimal submission
strategies of bid and ask orders in such a limit order book.
The pricing strategies of dealers have been studied extensively in the microstruc-
ture literature. The two most often addressed sources of risk facing the dealer are
(i) the inventory risk arising from uncertainty in the asset’s value and (ii) the asym-
metric information risk arising from informed traders. Useful surveys of their results
can be found in Biais et al. [1], Stoll [13] and a book by O’Hara [10]. In this paper,
we will focus on the inventory eﬀect. In fact, our model is closely related to a paper
1


<!-- PAGE 2 -->

by Ho and Stoll [6], which analyses the optimal prices for a monopolistic dealer in
a single stock. In their model, the authors specify a ’true’ price for the asset, and
derive optimal bid and ask quotes around this price, to account for the eﬀect of the
inventory. This inventory eﬀect was found to be signiﬁcant in an empirical study of
AMEX Options by Ho and Macris [5]. In another paper by Ho and Stoll [7], the prob-
lem of dealers under competition is analyzed and the bid and ask prices are shown to
be related to the reservation (or indiﬀerence) prices of the agents. In our framework,
we will assume that our agent is but one player in the market and the ’true’ price is
given by the market mid-price.
Of crucial importance to us will be the arrival rate of buy and sell orders that
will reach our agent. In order to model these arrival rates, we will draw on recent
results in econophysics.
One of the important achievements of this literature has
been to explain the statistical properties of the limit order book (see Bouchaud et al.
[2], Potters and Bouchaud [11], Smith et al. [12], Luckock [8]). The focus of these
studies has been to reproduce the observed patterns in the markets by introducing
’zero intelligence’ agents, rather than modeling optimal strategies of rational agents.
One possible exception is the work of Luckock [8], who deﬁnes a notion of optimal
strategies, without resorting to utility functions. Though our objective is diﬀerent to
that of the econophysics literature, we will draw on their results to infer reasonable
arrival rates of buy and sell orders. In particular, the results that will be most useful
to us are the size distribution of market orders (Gabaix et al. [3], Maslow and Mills
[9]) and the temporary price impact of market orders (Weber and Rosenow [14],
Bouchaud et al. [2]).
Our approach, therefore, is to combine the utility framework of the Ho and Stoll
approach with the microstructure of actual limit order books as described in the
econophysics literature. The main result is that the optimal bid and ask quotes are
derived in an intuitive two-step procedure. First, the dealer computes a personal
indiﬀerence valuation for the stock, given his current inventory. Second, he calibrates
his bid and ask quotes to the limit order book, by considering the probability with
which his quotes will be executed as a function of their distance from the mid-price.
In the balancing act between the dealer’s personal risk considerations and the market
environment lies the essence of our solution.
The paper is organized as follows. In section 2, we describe the main building
blocks for the model: the dynamics of the mid-market price, the agent’s utility ob-
jective and the arrival rate of orders as a function of the distance to the mid-price. In
section 3, we solve for the optimal bid and ask quotes, and relate them to the reserva-
tion price of the agent, given his current inventory. We then present an approximate
solution, numerically simulate the performance of our agent’s strategy and compare
its Proﬁt and Loss (P&L) proﬁle to that of a benchmark strategy.
2


<!-- PAGE 3 -->

2
The model
2.1
The mid-price of the stock
For simplicity, we assume that money market pays no interest. The mid-market price,
or mid-price, of the stock evolves according to
dSu = σdWu
(2.1)
with initial value St = s. Here Wt is a standard one-dimensional Brownian Motion
and σ is constant.1 Underlying this continuous-time model is the implicit assumption
that our agent has no opinion on the drift or any autocorrelation structure for the
stock.
This mid-price will be used solely to value the agent’s assets at the end of the
investment period.
He may not trade costlessly at this price, but this source of
randomness will allow us to measure the risk of his inventory in stock. In section 2.4
we will introduce the possibility to trade through limit orders.
2.2
The optimizing agent with ﬁnite horizon
The agent’s objective is to maximize the expected exponential utility of his P&L
proﬁle at a terminal time T.
This choice of convex risk measure is particularly
convenient, since it will allow us to deﬁne reservation (or indiﬀerence) prices which
are independent of the agent’s wealth.
We ﬁrst model an inactive trader who does not have any limit orders in the market
and simply holds an inventory of q stocks until the terminal time T. This ”frozen
inventory” strategy will later prove to be useful in the case when limit orders are
allowed. The agent’s value function is
v(x, s, q, t) = Et[−exp(−γ(x + qST)]
where x is the initial wealth in dollars. This value function can be written as
v(x, s, q, t) = −exp(−γx) exp(−γqs) exp
γ2q2σ2(T −t)
2

(2.3)
which shows us directly its dependence on the market parameters.
1We choose this model over the standard geometric Brownian motion to ensure that the utility
functionals introduced in the sequel remain bounded. In practical applications, we could also use a
dimensionless model such as
dSu
Su
= σdWu
(2.2)
with inital value St = s. To avoid mathematical inﬁnities, exponential utility functions could be
modiﬁed to a standard mean/variance objective with the same Taylor-series expansion. The essence
of the results would remain. More details regarding the model (2.2) with mean/variance utility are
given in the appendix.
3


<!-- PAGE 4 -->

We may now deﬁne the reservation bid and ask prices for the agent. The reserva-
tion bid price is the price that would make the agent indiﬀerent between his current
portfolio and his current portfolio plus one stock. The reservation ask price is deﬁned
similarly below. We stress that this is a subjective valuation from the point of view
of the agent and does not reﬂect a price at which trading should occur.
Deﬁnition 1. Let v be the value function of the agent. His reservation bid price rb is
given implicitly by the relation
v(x −rb(s, q, t), s, q + 1, t) = v(x, s, q, t).
(2.4)
The reservation ask price ra solves
v(x + ra(s, q, t), s, q −1, t) = v(x, s, q, t).
(2.5)
A simple computation involving equations (2.3), (2.4) and (2.5) yields a closed-
form expression for the two prices
ra(s, q, t) = s + (1 −2q)γσ2(T −t)
2
(2.6)
and
rb(s, q, t) = s + (−1 −2q)γσ2(T −t)
2
(2.7)
in the setting where no trading is allowed. We will refer to the average of these two
prices as the reservation or indiﬀerence price
r(s, q, t) = s −qγσ2(T −t),
given that the agent is holding q stocks. This price is an adjustment to the mid-
price, which accounts for the inventory held by the agent. If the agent is long stock
(q > 0), the reservation price is below the mid-price, indicating a desire to liquidate
the inventory by selling stock. On the other hand, if the agent is short stock (q < 0),
the reservation price is above the mid-price, since the agent is willing to buy stock at
a higher price.
2.3
The optimizing agent with inﬁnite horizon
Because of our choice of a terminal time T at which we measure the performance of
our agent, the reservation price (2.2) depends on the time interval (T −t). Intuitively,
the closer our agent is to time T, the less risky his inventory in stock is, since it can
be liquidated at the mid-price ST. In order to obtain a stationary version of the
reservation price, we may consider an inﬁnite horizon objective of the form
¯v(x, s, q) = E
Z ∞
0
−exp(−ωt) exp(−γ(x + qSt))dt

.
4


<!-- PAGE 5 -->

The stationary reservation prices (deﬁned in the same way as in Deﬁnition 1) are
given by
¯ra(s, q) = s + 1
γ ln

1 + (1 −2q)γ2σ2
2ω −γ2q2σ2

and
¯rb(s, q) = s + 1
γ ln

1 + (−1 −2q)γ2σ2
2ω −γ2q2σ2

,
where ω > 1
2γ2σ2q2.
The parameter ω may therefore be interpreted as an upper bound on the inventory
position our agent is allowed to take. The natural choice of ω = 1
2γ2σ2(qmax + 1)2
would ensure that the prices deﬁned above are bounded.
2.4
Limit orders
We now turn to an agent who can trade in the stock through limit orders that he sets
around the mid-price given by (2.1). The agent quotes the bid price pb and the ask
price pa, and is committed to respectively buy and sell one share of stock at these
prices, should he be ”hit” or ”lifted” by a market order. These limit orders pb and pa
can be continuously updated at no cost. The distances
δb = s −pb
and
δa = pa −s
and the current shape of the limit order book determine the priority of execution
when large market orders get executed.
For example, when a large market order to buy Q stocks arrives, the Q limit
orders with the lowest ask prices will automatically execute. This causes a temporary
market impact, since transactions occur at a price that is higher than the mid-price.
If pQ is the price of the highest limit order executed in this trade, we deﬁne
∆p = pQ −s
to be the temporary market impact of the trade of size Q. If our agent’s limit order
is within range of this market order, i.e. if δa < ∆p, his limit order will be executed.
We assume that market buy orders will ”lift” our agent’s sell limit orders at
Poisson rate λa(δa), a decreasing function of δa. Likewise, orders to sell stock will
”hit” the agent’s buy limit order at Poisson rate λb(δb), a decreasing function of δb.
Intuitively, the further away from the mid-price the agent positions his quotes, the
less often he will receive buy and sell orders.
The wealth and inventory are now stochastic and depend on the arrival of market
sell and buy orders. Indeed, the wealth in cash jumps every time there is a buy or
sell order
dXt = padNa
t −pbdNb
t
5


<!-- PAGE 6 -->

where Nb
t is the amount of stocks bought by the agent and Na
t is the amount of stocks
sold. Nb
t and Na
t are Poisson processes with intensities λb and λa. The number of
stocks held at time t is
qt = Nb
t −Na
t .
The objective of the agent who can set limit orders is
u(s, x, q, t) = max
δa,δb Et[−exp(−γ(XT + qTST)))].
Notice that, unlike the setting described in the previous subsection, the agent controls
the bid and ask prices and therefore indirectly inﬂuences the ﬂow of orders he receives.
Before turning to the solution of this problem, we consider some realistic functional
forms for the intensities λa(δa) and λb(δb) inspired by recent results in the econophysics
literature.
2.5
The trading intensity
One of the main focuses of the econophysics community has been to describe the laws
governing the microstructure of ﬁnancial markets. Here, we will be focussing on the
results which address the Poisson intensity λ with which a limit order will be executed
as a function of its distance δ to the mid-price. In order to quantify this, we need to
know statistics on (i) the overall frequency of market orders (ii) the distribution of
their size and (iii) the temporary impact of a large market order. Aggregating these
results suggests that λ should decay as an exponential or a power law function.
For simplicity, we assume a constant frequency Λ of market buy or sell orders.
This could be estimated by dividing the total volume traded over a day by the average
size of market orders on that day.
The distribution of the size of market orders has been found by several studies to
obey a power law. In other word, the density of market order size is
f Q(x) ∝x−1−α
(2.8)
for large x, with α = 1.53 in Gopikrishnan et al. [4] for U.S. stocks, α = 1.4 in
Maslow and Mills [9] for shares on the NASDAQ and α = 1.5 in Gabaix et al. [3] for
the Paris Bourse.
There is less consensus on the statistics of the market impact in the econophysics
literature. This is due to a general disagreement over how to deﬁne it and how to
measure it. Some authors ﬁnd that the change in price ∆p following a market order
of size Q is given by
∆p ∝Qβ
(2.9)
where β = 0.5 in Gabaix et al. [3] and β = 0.76 in Weber and Rosenow [14]. Potters
and Bouchaud [11] ﬁnd a better ﬁt to the function
∆p ∝ln(Q).
(2.10)
6


<!-- PAGE 7 -->

Aggregating this information, we may derive the Poisson intensity at which our
agent’s orders are executed. This intensity will depend only on the distance of his
quotes to the mid-price, i.e. λb(δb) for the arrival of sell orders and λa(δa) for the
arrival of buy orders. For instance, using (2.8) and (2.10), we derive
λ(δ)
= ΛP(∆p > δ)
= ΛP(ln(Q) > Kδ)
= ΛP(Q > exp(Kδ))
= Λ
R ∞
exp(Kδ) x−1−αdx
= A exp(−kδ)
(2.11)
where A = Λ/α and k = αK. In the case of a power price impact (2.9), we obtain
an intensity of the form
λ(δ) = Bδ−α
β .
Alternatively, since we are interested in short term liquidity, the market impact
function could be derived directly by integrating the density of the limit order book.
This procedure is described in Smith et al. [12] and Weber and Rosenow [14] and
yields what is sometimes called the ”virtual” price impact.
3
The solution
3.1
Optimal bid and ask quotes
Recall that our agent’s objective is given by the value function
u(s, x, q, t) = max
δa,δb Et[−exp(−γ(XT + qTST)))]
(3.1)
where the optimal feedback controls δa and δb will turn out to be time and state
dependent. This type of optimal dealer problem was ﬁrst studied by Ho and Stoll [6].
One of the key steps in their analysis is to use the dynamic programming principle
to show that the function u solves the following Hamilton-Jacobi-Bellman equation







ut + 1
2σ2uss + maxδb λb(δb)

u(s, x −s + δb, q + 1, t) −u(s, x, q, t)

+ maxδa λa(δa) [u(s, x + s + δa, q −1, t) −u(s, x, q, t)] = 0
u(s, x, q, T) = −exp(−γ(x + qs)).
The solution to this nonlinear PDE is continuous in the variables s, x and t and
depends on the discrete values of the inventory q. Due to our choice of exponential
utility, we are able to simplify the problem with the ansatz
u(s, x, q, t) = −exp(−γx) exp(−γθ(s, q, t)).
(3.2)
7


<!-- PAGE 8 -->

Direct substitution yields the following equation for θ









θt + 1
2σ2θss −1
2σ2γθ2
s
+ maxδb
h
λb(δb)
γ
[1 −eγ(s−δb−rb)]
i
+ maxδa
h
λa(δa)
γ
[1 −e−γ(s+δa−ra)]
i
= 0
θ(s, q, T) = qs.
(3.3)
Applying the deﬁnition of reservation bid and ask prices (given in Section 2.2) to the
ansatz (3.2), we ﬁnd that rb and ra depend directly on this function θ. Indeed,
rb(s, q, t) = θ(s, q + 1, t) −θ(s, q, t)
(3.4)
is the reservation bid price of the stock, when the inventory is q and
ra(s, q, t) = θ(s, q, t) −θ(s, q −1, t)
(3.5)
is the reservation ask price,when the inventory is q. From the ﬁrst order optimality
condition in (3.9), we obtain the optimal distances δb and δa. They are given by the
implicit relations
s −rb(s, q, t) = δb −1
γ ln
 
1 −γ λb(δb)
∂λb
∂δ (δb)
!
(3.6)
and
ra(s, q, t) −s = δa −1
γ ln
 
1 −γ λa(δa)
∂λa
∂δ (δa)
!
.
(3.7)
In summary, the optimal bid and ask quotes are obtained through an intuitive,
two step procedure. First, we solve the PDE (3.3) in order to obtain the reservation
bid and ask prices rb(s, q, t) and ra(s, q, t). Second, we solve the implicit equations
(3.6) and (3.7) and obtain the optimal distances δb(s, q, t) and δa(s, q, t) between the
mid-price and optimal bid and ask quotes. This second step can be interpreted as a
calibration of our indiﬀerence prices to the current market supply λb and demand λa.
3.2
Asymptotic expansion in q
The main computational diﬃculty lies in solving equation (3.3). The order arrival
terms (i.e. the terms to be maximized in the expression) are highly non-linear and
may depend on the inventory. We therefore suggest an asymptotic expansion of θ in
the inventory variable q, and a linear approximation of the order arrival terms. In
the case of symmetric, exponential arrival rates
λa(δ) = λb(δ) = Ae−kδ
(3.8)
the indiﬀerence prices ra(s, q, t) and rb(s, q, t) coincide with their ”frozen inventory”
values, as described in section 2.2.
8


<!-- PAGE 9 -->

Substituting the optimal values given by equations (3.6) and (3.7) into (3.3) and
using the exponential arrival rates, we obtain



θt + 1
2σ2θss −1
2σ2γθ2
s +
A
k+γ(e−kδa + e−kδb) = 0
θ(s, q, T) = qs.
(3.9)
Consider an asymptotic expansion in the inventory variable
θ(q, s, t) = θ0(s, t) + qθ1(s, t) + 1
2q2θ2(s, t) + . . .
(3.10)
The exact relations for the indiﬀerence bid and ask prices, (3.4) and (3.5), yield
ra(s, q, t) = θ1(s, t) + (1 −2q)θ2(s, t) + . . .
(3.11)
and
rb(s, q, t) = θ1(s, t) + (−1 −2q)θ2(s, t) + . . .
(3.12)
Using equations (3.11) and (3.12), along with the optimality conditions (3.6) and(3.7),
we ﬁnd that the optimal pricing strategy amounts to quoting a spread of
δa + δb = 2θ2(s, t) + 2
γ ln(1 + γ
k)
(3.13)
around the reservation price given by
r(s, q, t) = ra + rb
2
= θ1(s, t) −2qθ2(s, t).
The term θ1 can be interpreted as the reservation price, when the inventory is zero.
The term θ2 may be interpreted as the sensitivity of the market maker’s quotes to
changes in inventory. For instance, if θ2 is large, accumulating a long position q > 0
will result in aggressively low quotes.
The bid-ask spread in (3.13) is independent of the inventory. This follows from
our assumption of exponential arrival rates. The spread consists of two components,
one that depends on the sensitivity to changes in inventory θ2 and one that depends
on the intensity of arrival of orders, through the parameter k.
Taking a ﬁrst order approximation of the order arrival term
A
k + γ (e−kδa + e−kδb) =
A
k + γ
 2 −k(δa + δb) + . . .

(3.14)
we notice that the linear term does not depend on the inventory q. Therefore, if we
substitute (3.10) and (3.14) into (3.9) and group terms of of order q, we obtain



θ1
t + 1
2σ2θ1
ss = 0
θ1(s, T) = s
(3.15)
9


<!-- PAGE 10 -->

whose solution is θ1(s, t) = s. Grouping terms of order q2 yields



θ2
t + 1
2σ2θ2
ss −1
2σ2γ(θ1
s)2 = 0
θ2(s, T) = 0.
(3.16)
whose solution is θ2 = 1
2σ2γ(T −t). Thus, for this linear approximation of the order
arrival term, we obtain the same indiﬀerence price
r(s, t) = s −qγσ2(T −t)
(3.17)
as for the ”frozen inventory” problem from section 2.2. We then set a bid/ask spread
given by
δa + δb = γσ2(T −t) + 2
γ ln(1 + γ
k)
(3.18)
around this indiﬀerence or reservation price. Note that if we had taken a quadratic ap-
proximation of the order arrival term, we would still obtain θ1 = s, but the sensitivity
term θ2(s, t) would solve a non-linear PDE.
Equations (3.17) and (3.18) thus provide us with simple expressions for the bid
and ask prices in terms of our model parameters. This approximate solution also
simpliﬁes the simulations we perform in the next section.
3.3
Numerical simulations
We now test the performance of our strategy, focussing primarily on the shape of the
P&L proﬁle and the ﬁnal inventory qT. We will refer to our strategy as the ”inventory”
strategy, and compare it to a benchmark strategy that is symmetric around the mid-
price, regardless of the inventory. This strategy, which we refer to as the ”symmetric”
strategy, uses the same spread as the inventory strategy, but centers it around the
mid-price, rather than the reservation price.
In practice, the choice of time step dt is a subtle one. On the one hand, dt must
be small enough so that the probability of multiple orders reaching our agent is small.
On the other hand, dt must be larger than the typical tick time, otherwise the agent’s
quotes will be updated so frequently that he will not see any orders (particularly if
his quotes are outside the market bid/ask spread).
As far as our simulation is concerned, we chose the following parameters: s = 100,
T = 1, σ = 2, dt = 0.005, q = 0, γ = 0.1, k = 1.5 and A = 140. The simulation is
obtained through the following procedure: at time t, the agent’s quotes δa and δb are
computed, given the state variables. At time t + dt, the state variables are updated.
With probability λa(δa)dt, the inventory variable decreases by one and the wealth
increases by s+δa. With probability λb(δb)dt, the inventory increases by one and the
wealth decreases by s−δb. The mid-price is updated by a random increment ±σ
√
dt.
Figure 1 illustrates the bid and ask quotes for one simulation of a stock path.
10


<!-- PAGE 11 -->

0
0.1
0.2
0.3
0.4
0.5
0.6
0.7
0.8
0.9
1
98.5
99
99.5
100
100.5
101
101.5
102
102.5
103
Time
Stock 
Price
Mid−market price
Price asked
Price bid
Indifference Price
Figure 1. The mid-price, indiﬀerence price and the optimal bid and ask quotes
Notice that, at time t = 0.25, the indiﬀerence price is higher than the mid-price,
indicating that the inventory position must be negative (or short stock). Since the
bid price is aggressively placed near the mid-price, our agent is more likely to buy
stock and the inventory quickly returns to zero by time t = 0.3. As we approach
the terminal time, the indiﬀerence price gets closer to the mid-price, and our agent’s
bid/ask quotes look more like a symmetric strategy. Indeed, when we are close to the
terminal time, our inventory position is considered less risky, since the mid-price is
less likely to move drastically.
We then run 1000 simulations to compare our ”inventory” strategy to the ”sym-
metric” strategy. This strategy uses the same bid/ask spread as the inventory strat-
egy, but centers it around the mid-price. For example, the performance of the sym-
metric strategy that quotes a bid/ask spread of $1.29 (corresponding to the optimal
agent with γ = 0.1) is displayed in Table 1. This symmetric strategy has a higher
return and higher standard deviation than the inventory strategy. The symmetric
strategy obtains a slightly higher return since it is centered around the mid-price,
and therefore receives a higher volume of orders than the inventory strategy. How-
ever, the inventory strategy obtains a P&L proﬁle with a much smaller variance, as
illustrated in the histogram in Figure 2.
Strategy
Spread
Proﬁt
std(Proﬁt)
Final q
std(Final q)
Inventory
1.29
62.94
5.89
0.10
2.80
Symmetric
1.29
67.21
13.43
-0.018
8.66
Table 1: 1000 simulations with γ = 0.1
11


<!-- PAGE 12 -->

Figure 2. γ = 0.1
The results of the simulations comparing the ”inventory” strategy for γ = 0.01
with the corresponding ”symmetric” strategy are displayed in Table 2. This small
value for γ represents an investor who is close to risk neutral. The inventory eﬀect is
therefore much smaller and the P&L proﬁles of the two strategies are very similar, as
illustrated in Figure 3. In fact, in the limit as γ →0 the two strategies are identical.
Strategy
Spread
Proﬁt
std(Proﬁt)
Final q
std(Final q)
Inventory
1.33
66.78
8.76
-0.02
4.70
Symmetric
1.33
67.36
13.40
-0.31
8.65
Table 2: 1000 simulations with γ = 0.01
Finally, we display the performance of the two strategies for γ = 0.5 in Table 3.
This choice corresponds to a very risk averse investor, who will go to great lengths to
avoid accumulating an inventory. This strategy produces low standard deviations of
proﬁts and ﬁnal inventory, but generates more modest proﬁts than the corresponding
symmetric strategy (see Figure 4).
Strategy
Spread
Proﬁt
std(Proﬁt)
Final q
std(Final q)
Inventory
1.15
33.92
4.72
-0.02
1.88
Symmetric
1.15
66.20
14.53
0.25
9.06
Table 3: 1000 simulations with γ = 0.5
12


<!-- PAGE 13 -->

Figure 3. γ = 0.01
Figure 4. γ = 0.5
Appendix
Herein, we consider the geometric Brownian motion
dSu
Su
= σdWu
with initial value St = s, and the mean/variance objective
V (x, s, q, t) = Et[(x + qST) −γ
2(qST −qs)2]
where x is the initial wealth in dollars. This value function can be written as
V (x, s, q, t) = x + qs + γq2s2
2

eσ2(T−t) −1

This yields reservation prices of the form
Ra(s, q, t) = s + (1 −2q)
2
γs2 
eσ2(T−t) −1

and
Rb(s, q, t) = s + (−1 −2q)
2
γs2 
eσ2(T−t) −1

.
These results are analogous to the ones obtained in section 2.2.
References
[1] B. Biais, L. Glosten and C. Spatt, The Microstructure of Stock Markets, Working
paper (2004).
13


<!-- PAGE 14 -->

[2] J.-P. Bouchaud, M. Mezard and M. Potters, Statistical Properties of Stock Order
Books: Empirical Results and Models, Quantitative Finance, 2 (2002) 251-256.
[3] X. Gabaix, P. Gopikrishnan, V. Plerou, H.E. Stanley, A Theory of Large Fluctu-
ations in Stock Market Activity, MIT Department of Economics Working Paper
No. 03-30.
[4] P. Gopikrishnan, V. Plerou, X. Gabaix and H.E. Stanley, Statistical Properties
of Share Volume Traded in Financial Markets, Physical Review E, 62 (2000)
R4493-R4496.
[5] T. Ho and R. Macris, Dealer Bid-Ask Quotes and Transaction Prices: An Em-
pirical Study of Some AMEX Options, Journal of Finance, 39, (1984) 23-45.
[6] T. Ho and H. Stoll, Optimal Dealer Pricing under Transactions and Return
Uncertainty, Journal of Financial Economics, 9 (1981) 47-73.
[7] T. Ho and H. Stoll, On Dealer Markets under Competition, Journal of Finance,
35 (1980) 259-267.
[8] H. Luckock, A Steady-State Model of the Continuous Double Auction, Quanti-
tative Finance, 3 (2003) 385-404.
[9] S. Maslow and M. Mills, Price Fluctuations from the Order Book Perspective:
Empirical Facts and a Simple Model, Physica A, 299 (2001) 234-246.
[10] M. O’Hara,
Market Microstructure Theory,
Blackwell,
Cambridge,
Mas-
sachusetts (1997).
[11] M. Potters and J.-P. Bouchaud, More Statistical Properties of Order Books and
Price Impact, Physica A: Statistical Mechanics and its Applications, 324 (2003)
133-140.
[12] E. Smith, J.D. Farmer, L. Gillemot and S. Krishnamurthy, Statistical Theory of
the Continuous Double Auction, Quantitative Finance, 3 (2003) 481-514.
[13] H.R. Stoll, Market Microstructure, Handbook of the Economics of Finance,
Edited by G.M. Constantinides et al. North Holland (2003).
[14] P. Weber and B. Rosenow, Order Book Approach to Price Impact, Quantitative
Finance, 5 (2005) 357 - 364.
14
