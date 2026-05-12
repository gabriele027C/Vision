---
source_file: "The Price Impact of Order Book Events.pdf"
total_pages: 32
---



<!-- PAGE 1 -->

Electronic copy available at: http://ssrn.com/abstract=1712822
The price impact of order book events
Rama Cont, Arseniy Kukanov and Sasha Stoikov
First version: 01 March 2011, This version: April 30, 2012
Abstract
We study the price impact of order book events - limit orders, market orders and can-
celations - using the NYSE TAQ data for 50 U.S. stocks. We show that, over short time
intervals, price changes are mainly driven by the order ﬂow imbalance, deﬁned as the imbal-
ance between supply and demand at the best bid and ask prices. Our study reveals a linear
relation between order ﬂow imbalance and price changes, with a slope inversely proportional
to the market depth. These results are shown to be robust to intraday seasonality eﬀects,
and stable across time scales and across stocks. This linear price impact model, together
with a scaling argument, implies the empirically observed “square-root” relation between the
magnitude of price moves and trading volume. However, the latter relation is found to be
noisy and less robust than the one based on order ﬂow imbalance. We discuss a potential ap-
plication of order ﬂow imbalance as a measure of adverse selection in limit order executions,
and demonstrate how it can be used to analyze intraday volatility dynamics.
The authors are grateful to Nikolaus Hautsch, Andrei Kirilenko, Albert (Pete) Kyle, Adrien
de Larrard, Costis Maglaras, Jeﬀrey Russell and Haowen Zhong for insightful comments and
discussions. We also thank conference participants of the SIAM Financial Mathematics & En-
gineering 2010 Meeting, Fourth Annual SoFiE Meeting, Regional SoFiE Meeting at Tinbergen
Institute, Modeling High Frequency Data in Finance 3 Conference for interesting questions and
comments.
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 2 -->

Electronic copy available at: http://ssrn.com/abstract=1712822
Contents
1
Introduction
2
1.1
Summary
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
3
1.2
Outline
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
4
2
Price impact model
4
2.1
Stylized order book . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
4
2.2
Model speciﬁcation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
7
3
Estimation and results
8
3.1
Data . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
8
3.2
Variables
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
9
3.3
Empirical ﬁndings
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
11
4
Applications
14
4.1
Monitoring adverse selection . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
14
4.2
Intraday volatility dynamics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
15
4.3
Volume and volatility
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
17
5
Conclusion
19
A Appendix: TAQ data processing
23
B Appendix: Robustness checks
24
B.1
Cross-sectional evidence . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
24
B.2
Transaction prices
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
29
B.3
Order ﬂow at higher order book levels . . . . . . . . . . . . . . . . . . . . . . . .
30
B.4
Choice of timescale . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
31
C Appendix: Proof of Proposition 1
32
1
Introduction
The availability of high-frequency records of trades and quotes has stimulated an extensive
empirical and theoretical literature on the relation between order ﬂow, liquidity and price move-
ments in order-driven markets. A particularly important issue for applications is the impact of
orders on prices: the optimal liquidation of a large block of shares, given a ﬁxed time horizon,
crucially involves assumptions on price impact (see Bertsimas and Lo [7], Almgren and Chriss
[2], Obizhaeva and Wang [40]). Understanding price impact is also important from a theoretical
perspective, since it is a fundamental mechanism of price formation.
Various aspects of price impact have been studied in the literature but there is little agree-
ment on how to model it [8], and the only consensus seems to be the intuitive notion that
imbalance between supply and demand moves prices. Theoretical studies draw a distinction
between instantaneous price impact of orders and its decay through time, and show that the
form of instantaneous impact has important implications. Huberman and Stanzl [27] show that
there are arbitrage opportunities if the instantaneous eﬀect of trades on prices is non-linear and
permanent. Gatheral [19] extends this analysis by showing that if the instantaneous price impact
function is non-linear, impact needs to decay in a particular way to exclude arbitrage and if it is
linear, it needs to decay exponentially. Bouchaud et al. [9] associated the decay of price impact
of trades with limit orders, arguing that there is a “delicate interplay between two opposite
2
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 3 -->

tendencies: strongly correlated market orders that lead to super-diﬀusion (or persistence), and
mean reverting limit orders that lead to sub-diﬀusion (or anti-persistence)”. This insight implies
that looking solely at trades, without including the eﬀect of limit orders amounts to ignoring an
important part of the price formation mechanism.
However, most of the empirical literature on price impact has primarily focused on trades.
One approach is to study the impact of “parent orders” gradually executed over time using
proprietary data (see Engle et. al [14], Almgren et. al [3]). Alternatively, empirical studies on
public data [16, 18, 20, 30, 31, 48, 42, 43] have analyzed the relation between the direction and
sizes of trades and price changes and typically conclude that the instantaneous price impact
of trades is an increasing, nonlinear function of their size. This focus on trades leaves out the
information in quotes, which provide a more detailed picture of price formation [15], and raises
a natural question: is volume of trades truly the best explanatory variable for price movements
in markets where many quote events can happen between two trades?
In our view, a price impact model that encompasses limit orders, market orders and cance-
lations, and relates their impact to the concurrent market liquidity would provide a more detailed
description of price formation. Obtaining such model is also desireable from the practical point
of view because modern order execution algorithms increasingly use limit orders and incorpo-
rate market state variables in their decisions. There is also ample empirical evidence that limit
orders play an important role in determining price dynamics. Arriving limit orders signiﬁcantly
reduce the impact of trades [49] and the concave shape of the price impact function changes
depending on the contemporaneous limit order arrivals [46]. The outstanding limit orders (also
known as market depth) signiﬁcantly aﬀect the impact of an individual trade ([32]), low depth is
associated with large price changes [50, 17], and depth inﬂuences the relation between trade sizes
and returns [24]. The emphasis in the aforementioned studies remains, however, on trades and
there are few empirical studies that focus on limit orders from the outset. Notable exceptions
are Engle & Lunde [15], Hautsch and Huang [25] who perform an impulse-response analysis of
limit and market orders, Hopman [26] who analyzes the impact of diﬀerent order categories over
30 minute intervals and Bouchaud et al. [12] who examine the impact of market orders, limit
orders and cancelations at the level of individual events.
1.1
Summary
We conduct an empirical investigation of the instantaneous impact of order book events – market
orders, limit orders and cancelations – on equity prices.
Although previous studies give a
relatively complex description of their impact, we show that their instantaneous eﬀect on prices
may be modeled parsimoniously through a single variable, the order ﬂow imbalance (OFI). This
variable represents the net order ﬂow at the best bid and ask and tracks changes in the size of
the bid and ask queues by
 increasing every time the bid size increases, the ask size decreases or the bid/ask prices
increase,
 decreases every time the bid size decreases, the ask size increases or the bid/ask prices
decrease.
Interestingly, this variable treats a market sell and a cancel buy of the same size as equivalent,
since they have the same eﬀect on the size of the best bid queue.
This aggregate variable
explains mid-price changes over short time scales in a linear fashion, for a large sample of
stocks, with an average R2 of 65%. In contrast, order ﬂows deeper in the order book do not
substantially contribute to price changes. Our model based on OFI relates prices, trades, limit
orders and cancelations in a simple way: it is linear, requires the estimation of a single price
impact coeﬃcient and it is robust across stocks and across timescales.
3
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 4 -->

Most of variability in the instantaneous price impact, both across time and across stocks is
explained by variations in market depth. In fact, we establish an exact inverse relation between
the two variables. The coeﬃcient of proportionality in that relation depends dramatically on
the depth deﬁnition, showing that arbitrary measures of market depth are biased proxies for
price impact and may lead to misleading conclusions on market liquidity.
The price impact coeﬃcient exhibits substantial intraday variablility coinciding with known
intraday patterns observed in spreads, market depth and price volatility [1, 5, 35, 39].
We
explain the diurnal eﬀects in price volatility using the volatility of order ﬂow imbalance and
market depth, as opposed to unobservable parameters previously invoked in the literature, such
as information asymmetry [38] or informativeness of trades [21]. The strong link between price
volatility and standard deviation of OFI suggests that our price impact coeﬃcient is a better
estimate of Kyle’s λ (a useful metric of liquidity [4, 33]) than traditional estimates based on
trades data. We also show that intraday price volatility is mainly driven by OFI and not by
trading volume. The positive correlation between price volatility and volume, widely conﬁrmed
by empirical studies [29], can be a statistical artifact due to aggregation of data over time, and
we establish how such spurious relation can arise in our model.
The OFI variable exhibits positive autocorrelation over short time scales, which can be
exploited to improve the quality of order executions. In particular, we show that a limit order ﬁll
is more likely to be followed with a price change in the same direction as the order ﬂow imbalance
before that ﬁll. For example, a limit sell order is more likely to be adversely selected when order
ﬂow imbalance is positive. Monitoring OFI can therefore help reduce adverse selection in limit
order ﬁlls.
1.2
Outline
The article is structured as follows. In Section 2, we specify a parsimonious model that links
stock price changes, order ﬂow imbalance and market depth and motivate it by a stylized example
of the order book. Section 3 describes our data and presents estimation results for our model.
Section 4 discusses potential applications of our results: in 4.1 we use order ﬂow imbalance as a
measure of adverse selection in limit order executions, in 4.2 we demonstrate how diurnal eﬀects
in depth and order ﬂow imbalance generate intraday patterns in price impact and price volatility,
and in 4.3 we show how a spurious relation between volume and the magnitude of price moves
emerges as a statistical artifact from our simple model. Section 5 presents our conclusions.
2
Price impact model
2.1
Stylized order book
To motivate our approach we ﬁrst consider a stylized example of the order book where the
instantaneous eﬀect of order book events can be explicitly computed.
Consider an order book in which the number of shares (depth) at each price level beyond
the best bid and ask is equal to D. Order arrivals and cancelations occur only at the best bid
and ask. Moreover, when bid (or ask) size reaches D, the next passive order arrives one tick
above (or below) the best quote, initializing a new best level. Consider a time interval [tk−1, tk]
and denote by Lb
k, Cb
k respectively the total size of buy orders that arrived to and canceled from
current best bid during that time interval. Also denote by Mb
k the total size of marketable buy
orders that arrived to current best ask, and by P b
k the bid price at time tk. The quantities
Ls
k, Cs
k, Ms
k for sell orders are deﬁned analogously and P s
k is the ask price.
In this simple order book model there exists a linear relation between order ﬂows
Lb,s
k , Cb,s
k , Mb,s
k
and price changes ∆P b,s
k
= (P b,s
k
−P b,s
k−1) (also illustrated on Figures 1-3):
4
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 5 -->

∆P b
k =
δ
Lb
k −Cb
k −Ms
k
D

(1)
∆P s
k = −δ
Ls
k −Cs
k −Mb
k
D

,
(2)
where δ is the tick size1. These relations are remarkably simple - they involve no parameters, the
impact of all order book events is additive and depends only on their net imbalance. Although
all of the subsequent analysis can be carried out separately for bid and ask prices, for simplicity
we consider mid-price changes normalized by tick size Pk = P b
k+P s
k
2δ
:
∆Pk = OFIk
2D
+ ϵk,
(3)
OFIk = Lb
k −Cb
k −Ms
k −Ls
k + Cs
k + Mb
k
(4)
where OFIk is the order ﬂow imbalance (or net order ﬂow) and ϵ is the truncation error. We
can also rewrite (3) as:
∆Pk = TIk
2D + ηk,
(5)
TIk = Mb
k −Ms
k
(6)
where TIk is the trade imbalance and ηk =
Lb
k−Cb
k−Ls
k+Cs
k
2D
+ ϵk.
When limit order activity
dominates, i.e. absolute values of terms |Lb,s
k |, |Cb,s
k | are much larger than |Mb,s
k |, the correlation
of price changes with TIk is weaker than with OFIk, because limit order submissions and
cancelations manifest as noise in (5).
1This is easily proven by induction over the number of price changes in [tk−1, tk]. The statement is clearly true
when there are no price changes or a single price change of ±δ. Since any price change of ±kδ consists of jumps
of size 1, we simply need to sum the order ﬂow imbalances across these jumps on the right side of the equation.
5
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 6 -->

Figure 1: Market sell orders remove Ms shares from the bid (gray squares represent net change
in the order book).
Figure 2: Market sell orders remove Ms shares from the bid, while limit buy orders add Lb
shares to the bid.
Figure 3: Market sell orders and limit buy cancels remove Ms + Cb shares from the bid, while
limit buy orders add Lb shares to the bid.
6
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 7 -->

2.2
Model speciﬁcation
Actual order books have complex dynamics: arrivals and cancelations occur at all price levels, the
depth distribution across levels has non-trivial features [43, 45, 52], and hidden orders together
with data-reporting issues create additional errors [6, 22]. Motivated by the stylized order book
example we assume a noisy relation between price changes and OFI, which holds locally for
short intervals of time [tk−1,i, tk,i] ⊂[Ti−1, Ti], where [Ti−1, Ti] are longer intervals.
∆Pk,i = βiOFIk,i + ϵk,i,
(7)
In this model βi is a price impact coeﬃcient for an i-th time interval and ϵk,i is a noise term
summarizing inﬂuences of other factors (e.g. deeper levels of the order book). We allow βi
and the distribution of ϵk,i to change with index i, because of well-known intraday seasonality
eﬀects. Our discussion from the previous section allows us to interpret
1
2βi as an implied order
book depth. The stylized order book model suggests that price impact coeﬃcient is inversely
related to market depth, and we consider the following model:
βi =
c
Dλ
i
+ νi,
(8)
where c, λ are constants and νi is a noise term. The stylized order book model corresponds to
c = 1
2, λ = 1. We also consider a relation between price changes and trades:
∆Pk,i = βT
i TIk,i + ηk,i,
(9)
but expect it to be much noisier than (7).
The speciﬁcation (7-8) may be regarded as a model of instantaneous price impact of order
book events, arriving within time interval [tk−1, tk]. An order submitted or canceled at time
τ ∈[tk−1, tk] contributes a signed quantity eτ to supply/demand. In any given time interval,
these contributions are likely be unbalanced, leading to an order ﬂow imbalance OFIk, which
aﬀects supply/demand and leads to a corresponding price adjustment. If an individual order
goes in the same direction as the majority of orders (sgn(eτ) = sgn(OFIk)), it reinforces the
concurrent order ﬂow imbalance and can aﬀect the price. If the order goes against the concurrent
order ﬂow imbalance (sgn(eτ) = −sgn(OFIk)), it is compensated by other orders and has an
instantaneous impact of zero. In our model all events (including trades) have a linear price
impact, on average equal to βi during the i-th interval. Their realized impact however depends
on the concurrent orders.
The idea that the concurrent limit order activity can make a diﬀerence in terms of trades’
impact was demonstrated in [46], where authors show that the shape of the price impact func-
tion essentially depends on the contemporaneous limit order activity. Our approach can also be
related to the model proposed in [12], where order book events have a linear impact on prices,
which depends on their signs and types2. The major diﬀerence of our model lies in the aggrega-
tion across time and events. As shown in [12], time series of individual order book events have
complicated auto- and cross-correlation structures, which typically vanish after 10 seconds. In
our data the autocorrelations at a timescale of 10 seconds are small and quickly vanish as well
(ACF plots for a representative stock are shown on Figure 4). Finally, the model used in [24]
for explaining the price impact of trades is similar to (9). Although the focus there is on trades,
authors allow the price impact coeﬃcient to depend on contemporaneous liquidity factors and
change through time.
2Note that in our case all order book events have the same average impact, equal to βi, regardless of their type.
As shown in [12], average impacts of diﬀerent event types are empirically very similar, allowing to reasonably
approximate them with a single number.
7
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 8 -->

At the same time, the linear relation (7) is diﬀerent from many earlier models that consider
only the eﬀect of transactions [18, 20, 31, 48, 42, 43]. Instead of modeling price impact of trades
as a (nonlinear) function of trade size, we show that the instantaneous price impact of a series of
events (including trades) is a linear function of their size after these events are aggregated into
a single imbalance variable. We will show that, ﬁrst, the eﬀect of trades on prices is adequately
captured by the order ﬂow imbalance and, second, that if one leaves out all events except trades,
the relation 7 leads to an apparent concave relation between the magnitude of price changes and
trading volume.
The next section provides an overview of the estimation results for our model.
Figure 4: ACF of the mid-price changes ∆Pk,i, the order ﬂow imbalance OFIk,i and the 5%
signiﬁcance bounds for the Schlumberger stock (SLB).
3
Estimation and results
3.1
Data
Our main data set consists of one calendar month (April, 2010) of trades and quotes data for
50 stocks. The stocks were selected by a random number generator from S&P 500 constituents,
which were obtained from Compustat. The data for individual stocks was obtained from the
TAQ consolidated quotes and TAQ consolidated trades databases3.
Consolidated quotes contain best bid/ask price changes and round-lot changes in best
bid/ask sizes. Quote data entries consist of a stock ticker, a timestamp (rounded to the nearest
second), bid price and size, ask price and size and various ﬂags including exchange ﬂag. Consol-
idated trade entries consist of timestamps, prices, sizes and various ﬂags. These two data sets
are often referred to as Level 1 data, as opposed to Level 2 data, which includes quote updates
deeper in the book, or information on individual orders.
At the same time TAQ data has important limitations - the timestamps are rounded to
the nearest second, and it may omit odd-lot trades and quotes. To perform several detailed
robustness checks we also use an auxilary data set consisting of NASDAQ ITCH 4.0 messages
for the same calendar month (April, 2010) for one representative stock from our main data
3The TAQ data were obtained through Wharton Research Data Services (WRDS).
8
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 9 -->

set (Schlumberger). This data is accessible through LOBSTER website4 which also provides
NASDAQ order book history for the selected stock. We used LOBSTER data for the top ﬁve
order book levels without any additional pre-processing.
The TAQ data was used to compute the National Best Bid and Oﬀer sizes and prices
(NBBO) at each quote update. We ﬁnd that the ratio between the number of NBBO quote
updates and the number of trades is roughly 40 to 1 in our data. Many empirical studies have
focused exclusively on trades rather than quotes, but the sheer diﬀerence in sizes of these data
sets suggests that more information may be conveyed by quotes than by trades.
Using the
exchange ﬂag, we also considered one exchange at a time and obtained similar empirical results.
3.2
Variables
Every observation of the bid and the ask consists of the bid price P b, the the bid queue size
qb (in number of shares), the ask price P s and size qs. We enumerate them by n and compute
diﬀerences betwen consecutive observations (P b
n, qb
n, P s
n, qs
n) as follows:
en = qb
n1{P bn≥P b
n−1} −qb
n−11{P bn≤P b
n−1} −qs
n1{P sn≤P s
n−1} + qs
n−11{P sn≥P s
n−1}
(10)
The variables en are signed contributions of order book events to supply/demand.
When a
passive buy order arrives, qb increases but P b remains the same, leading to en = qb
n −qb
n−1 which
is the size of that order. If qb decreases, we have en = qb
n −qb
n−1, representing the size of a
marketable sell order or buy order cancelation. If P b changes, then en = qb
n or en = −qb
n−1,
representing respectively the size of a price-improving order or the last order in the queue that
that was removed. Symmetric computations are done for the ask side.
We use two uniform time grids {T0, . . . , TI} and {t0,0, . . . , tI,K} with time steps Ti −Ti−1 =
30 minutes and tk,i −tk−1,i = ∆t = 10 seconds5. Within each long time interval [Ti−1, Ti] we
compute 180 price changes and order ﬂow imbalances indexed by k:
∆Pk,i =
P b
N(tk,i) + P s
N(tk,i)
2δ
−
P b
N(tk−1,i) + P s
N(tk−1,i)
2δ
(11)
OFIk,i =
N(tk,i)
X
n=N(tk−1,i)+1
en,
(12)
where N(tk−1,i) + 1 and N(tk,i) are the index of the ﬁrst and the last order book event in the
interval [tk−1,i, tk,i]. The tick size δ is equal to 1 cent in our data. Note that in our empirical
study OFI is computed from ﬂuctuations in best bid/ask prices and their sizes according to
(12), because data on individual orders is not available in our main dataset. If that data is
avalable, OFI can be computed according to (4). We believe that a computation based on
(4) can lead to better empirical results because aggressive order terms Mb, Ms will capture
information on hidden orders and unreported odd-lot sized orders within the spread, to the
extent that aggressive orders interact with hidden orders. Since TAQ data reports only round-
lot sized quote changes, we note that units of OFI are round lots (100 shares), and assume in
(12) that both sides of the market are equally aﬀected by missing quote updates6.
We deﬁne trade imbalance during a time interval [tk−1,i, tk,i] as the diﬀerence between
volumes of buyer- and seller-initiated trades during that interval, and also deﬁne trading volume
within that time interval:
4http://lobster.wiwi.hu-berlin.de/Lobster/about/About WhatIsLOBSTER.jsp
5results for other timescales are reported in the appendix
6As we demonstrate in the appendix, neither missing odd-lot sized observations nor potential mis-sequencing
of quote updates across diﬀerent exchanges during NBBO computation change our qualitative ﬁndings.
9
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 10 -->

TIk,i =
N(tk,i)
X
n=N(tk−1,i)+1
bn −sn
V OLk,i =
N(tk,i)
X
n=N(tk−1,i)+1
bn + sn
(13)
where bn, sn are sizes of buyer- and seller-initiated trades (in round lots) that occured at the
n-th quote (equal to zero if no trade occured at that quote). In contrast with TI, the OFI
measure computed using (12) does not hinge on trade classiﬁcation, which is known to be prob-
lematic for TAQ data (see appendix for more details on matching trades with quotes and trade
classiﬁcation). Whereas previous studies [11, 20, 24, 31, 42, 48] focused on trade imbalance7,
the order ﬂow imbalance is a more general measure. It encompasses eﬀects of all order book
events, including trades.
For each interval [Ti−1, Ti] we also estimate depth by averaging the bid/ask queue sizes
right before or right after a price change, consistently with the deﬁnition of depth in the stylized
order book model:
Di = 1
2


N(Ti)
P
n=N(Ti−1)+1

qb
n1{P bn<P b
n−1} + qb
n−11{P bn>P b
n−1}

N(Ti)
P
n=N(Ti−1)+1
1{P bn̸=P b
n−1}
+
N(Ti)
P
n=N(Ti−1)+1

qs
n1{P sn>P s
n−1} + qs
n−11{P sn<P s
n−1}

N(Ti)
P
n=N(Ti−1)+1
1{P sn̸=P s
n−1}


7Hopman [26] computes the supply/demand imbalance based on limit orders and trades, but not cancelations.
10
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 11 -->

3.3
Empirical ﬁndings
This section reports detailed results for a representative stock, Schlumberger (SLB) and some
average results across stocks. Detailed results for other stocks in our sample are presented in the
appendix. During the sample period the average price of Schlumberger stock was 67.94 dollars
and the average daily volume was 947.6 million shares. The daily average number of NBBO
quote updates is about 440 thousands, and the average daily number of trades is around 10
thousands. The average spread is one cent, its 95-th percentile is 2 cents and the average best
NBBO quote size is 39 round lots (3900 shares).
The model (7) is estimated by an ordinary least squares regression:
∆Pk,i = ˆαi + ˆβiOFIk,i + ˆϵk,i,
(14)
with separate half-hour subsamples indexed by i.
Figure 5 presents a scatter plot of ∆Pk,i
against OFIk,i for one of such subsamples.
In general we ﬁnd that ˆβi is statistically signiﬁcant8 in 98% of samples, and ˆαi is signiﬁcant
in 10% of samples, which is close to the Type-I error rate. The average t-statistics for ˆαi, ˆβi are
respectively -0.21 and 16.27 for SLB (cross-sectional averages are -0.02 and 12.08). To check for
higher order/nonlinear dependence we estimate an augmented regression:
∆Pk,i = ˆαQ
i + ˆγiOFIk,i + ˆγQ
i OFIk,i|OFIk,i| + ˆϵQ
k,i,
(15)
The coeﬃcients ˆγQ
i have an average t-statistic of -0.32 across stocks and are statistically signif-
icant only in 17% of our samples. We reject the hypothesis of quadratic (convex or concave)
instantaneous price impact, and take this as strong evidence for a linear price impact model (7),
because other kinds of non-linear dependence would likely be picked up by this quadratic term.
Figure 5: Scatter plot of ∆Pk,i against OFIk,i for the Schlumberger stock (SLB), 04/01/2010
11:30-12:00pm.
The goodness of ﬁt is surprising for high-frequency data, with an R2 of 76% for SLB and
65% on average across stocks9, suggesting that a one-parameter linear model (7) performs well
8Given a relatively large number of observations we use the z-test with a 95% signiﬁcance level. Since regression
residuals demonstrate heteroscedasticity and autocorrelation, Newey-West standard errors are used to compute
t-statistics.
9We note that OFI includes the contributions en of price-changing order book events, leading to a possible
11
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 12 -->

regardless of stock-speciﬁc features, such as average spread, depth or price level. The deﬁnition
of R2 as a percentage of explained variance has an interesting consequence in our case. Since
OFI is constructed from order book events taking place only at the best bid/ask, our results
show that activity at the top of the order book is the most important factor driving price
changes. In the appendix we conﬁrm this by showing that order ﬂow imbalances from deeper
order book levels only marginally contribute to short-term price dynamics. Even though large
price movements sometimes occur at this timescale, they mostly correspond to large readings
of OFI. Figure 6 conﬁrms this by demonstrating a relatively low level of excess kurtosis in
regression residuals.
Figure 6: Distribution of excess kurtosis in the residuals ˆϵk,i across stocks and time.
When the amount of passive order submissions and cancelations is much larger than the
amount of trades, the stylized order book model predicts that trade imbalance TI explains
price changes signiﬁcantly worse than OFI. To empirically conﬁrm this we estimate following
regressions using the same half-hour subsamples 10:
∆Pk,i = ˆαT
i + ˆβT
i TIk,i + ˆηk,i
(16a)
∆Pk,i = ˆαD
i + ˆθO
i OFIk + ˆθT
i TIk,i + ˆϵD
k,i
(16b)
When either OFI or TI variable is taken individually, that variable has a statistically signiﬁcant
correlation with price changes. The average t-statistics of slope coeﬃcients in simple regressions
(14, 16a) are, correspondingly 16.27 and 5.31 for SLB (cross-sectional averages are 12.08 and
5.08). The average R2 for the two regressions are 65% and 32%, respectively, conﬁrming the
prediction that relation between price changes and trade imbalance is more noisy. When the
two variables are used in a multiple regression (16b), the dependence of price changes on trade
imbalance becomes much weaker. The average t-statistic of TI coeﬃcient drops to 1.56 for SLB
endogeneity in the regression (14). This problem is inherent to all price impact modeling, because the explanatory
variables (events or trades) sometimes mechanically lead to price changes.
To test that the high R2 in our
regressions is not due to this endogeneity, we estimated (14) on a subsample of stocks, excluding the price-
changing events from OFI. With this change the R2 declined, but remained high, in the 35%-60% region.
10These regressions contain only linear terms, because we found no evidence of non-linear price impacts in our
data (for neither OFI nor TI).
12
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 13 -->

(1.51 across stocks) and it remains statistically signiﬁcant in only 47% of SLB samples (43% of
all stock samples). The dependence on OFI remains strong with an average t-statistic 13.91 for
SLB (9.53 across stocks), and the coeﬃcient is statistically signiﬁcant in almost all samples. We
conclude that OFI explains price movements better than trade imbalance, and OFI is a more
general measure of supply/demand imbalance because it adequately includes the eﬀect of trade
imbalance.
Finally, we use time series of Di and ˆβi for each stock to estimate the relation (8) with the
following two regressions:
log ˆβi =
ˆ
αL,i −ˆλ log Di + ˆϵL,i
(17)
ˆβi =
ˆ
αM,i +
ˆc
Dˆλ
i
+ ˆϵM,i
(18)
Both regressions are estimated using ordinary least squares11. For SLB we ﬁnd ˆc = 0.56, ˆλ =
1.08 and an R2 of (17) is 92%. The results for all stocks are shown in Table 4. We observe
that depth signiﬁcantly correlates with price impact coeﬃcients for the vast majority of stocks,
conﬁrming our intuition that
1
2βi is the implied order book depth. Interestingly, estimates ˆc, ˆλ
across stocks are very close to values predicted by the stylized order book model. With the
t-statistics12 in Table 4 the null hypotheses {c = 0.5} and {λ = 1} cannot be rejected for
most stocks based on conventional signiﬁcance levels. The restricted model with λ = 1 also
demonstrates a good quality of ﬁt, making this a good approximation.
Figure 7 illustrates
these results with a log-log scatter plot for Di and ˆβi. Some stocks (namely APOL, AZO and
CME) have poor ﬁts in regression (17), mainly due to outliers in the dependent variable. After
removing these outliers and re-estimating the regression, the estimates ˆc, ˆλ for these stocks fell
in line with estimates for other stocks.
To assess the stability of these ﬁndings, we re-estimated (17,18) with observations pooled
across days but not across intraday time intrervals, resulting in 13 estimates ˆci, ˆλi for each stock.
Although these estimates demonstrate some diurnal variablility, they are relatively stable and
most of variability in price impact coeﬃcients is explained by variations in depth (e.g. see Figure
9).
We repeated the analysis with diﬀerent depth variables, taking Di to be equal to arithmetic
or geometric average of queue sizes over the i-th time interval. Overall, the results were the same,
except for the level of ˆc estimates, which were about 40% lower across stocks for the arithmetic
average depth, and even lower for the geometric average. The systematic diﬀerence in these
coeﬃcients implies that taking an arbitrary measure of depth (such as arithmetic average of
queue sizes) as a proxy of price impact may lead to signiﬁcant biases, i.e. one would dramatically
under- or over-estimate price impact in a given stock. Instead of looking at arbitrary depth
measures, we suggest computing price impact coeﬃcients βi and/or implied depth
1
2βi to precisely
characterize price sensitivity to order ﬂow.
11We note that an estimate ˆλi is used in regression (18). This “plug-in” approach leads to potential errors
in explanatory variable, and standard errors for ˆc may be underestimated. However, the good quality of ﬁt in
regression (17) with an average R2 of 76% indicates that ˆλi are estimated with good presicion. We believe that
errors in variable
1
Dˆλ
i
are small and do not aﬀect our results.
12Since the residuals of these regressions appear to be autocorrelated, the t-statistics are computed with Newey-
West standard errors.
13
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 14 -->

Figure 7: Log-log scatter plot of the price impact coeﬃcient estimate ˆβi against average market
depth Di for the Schlumberger stock (SLB).
4
Applications
4.1
Monitoring adverse selection
Time intervals that are involved in modern high-frequency trading applications are usually so
short that price changes are relatively infrequent events. Therefore price changes provide a very
coarse and limited description of market dynamics. However, OFI tracks best bid and ask queues
and ﬂuctuates on a much faster timescale than prices. It incorporates information about build-
ups and depletions of order queues and it can be used to interpolate market dynamics between
price changes (see Figure 8 for example). Our results conﬁrm that such interpolation is in fact
valid because OFI closely approximates price changes over short time intervals (e.g. results for
50 millisecond time intervals are shown in the appendix). To study one possible application of
OFI for high-frequency trading we turn to our auxilary dataset, because it contains accurate
timestamps up to a millisecond.
Given the strong link between OFI and price changes, and the positive autocorrelation
of OFI over short time intervals (see Figure 4), we propose to use it as a measure of adverse
selection in the order ﬂow. For example, when a limit order is ﬁlled, and its execution was
preceded by positive OFI, a positive price change is more likely to happen after the limit order
execution. This is because the pre-execution positive OFI is likely to persist in the future, and
can lead to a post-execution positive price change. For a limit sell order a positive post-execution
price change implies that the order was executed at a loss, i.e. adversely selected.
To test our hypothesis, we consider all limit order executions in our auxilary dataset.
For each execution we compute the pre-execution order ﬂow imbalance OFIpre
k
and the post-
execution mid price change ∆P post
k
. The pre-execution order ﬂow imbalance is computed from
best bid and ask quote updates with timestamps in [tk −200, tk −1] milliseconds, where tk is
the time of the k-th limit order execution. Similarly the post-execution price change is deﬁned
as the diﬀerence in mid-quote prices between tk + 200 milliseconds and tk13 . Then we consider
30-minute subsamples of data indexed by i, and estimate the following regression:
∆P post
k,i
= αp
i + βp
i OFIpre
k,i + ϵp
k,i,
(19)
13If there are multiple quotes with timestamp tk + 200 or tk, we take the last one.
14
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 15 -->

Figure 8: Price dynamics and cumulative OFI on NASDAQ for a 1-second time interval starting
at 11:16:39.515 on 04/28/2010, Schlumberger stock (SLB).
The average R2 of these regressions across a month is 2.93%, the average t-statistic14 of βp
i is
2.68 and this coeﬃcient is signiﬁcant at a 5% level in 63% of subsamples. The average βp
i is
0.0105. We conclude that pre-execution OFI are positively correlated with post-execution price
changes.
We also estimated regression (19) with 50- and 100-millisecond time intervals for pre- and
post-execution variables, and obtained similar results, with stronger correlations for smaller
time intervals15. When we split OFIpre
k,i into multiple order ﬂow imbalance variables over non-
overlapping subintervals of [tk −200, tk −1], we ﬁnd that only the variable closest to tk - the
execution time - is statistically signiﬁcant and positively correlated with post-execution price
change. These results suggest that limit order traders need to actively monitor order ﬂows and
react to emerging order ﬂow imbalances as quickly as possible to avoid being adversely selected.
4.2
Intraday volatility dynamics
The link between price impact and market depth established here has important implications
for intraday volatility. Market depth is known to follow a predictable diurnal pattern ([1], [35]),
and equation (8) implies that instantaneous price impact must also have a predictable intraday
pattern. To demonstrate it, we averaged ˆβi for each stock and each intraday half-hour interval
across days, resulting in diurnal eﬀects for that stock, normalized these eﬀects by a grand average
ˆβi for that stock and averaged normalized diurnal eﬀects across stocks. The same procedure was
repeated for depths Di. We also re-estimated (17,18) with observations pooled across days but
not across intraday time intrervals, resulting in 13 estimates ˆλi, ˆci for each stock. The overall
average diurnal eﬀects for these quantities are shown on Figure 9.
We found that between 9:30 and 10am the depth is two times lower than on average,
indicating that the market is relatively shallow. In a shallow market, incoming orders can easily
aﬀect mid-prices and price impact coeﬃcients between 9:30 and 10am are in fact two times
14Here we also use Newey-West standard errors because residuals demonstrate signiﬁcant autocorrelation.
15For instance, with 50-millisecond time intervals the average t-statistic of βp
i is 3.41 and this coeﬃcient is
signiﬁcant in 75% of samples. The average R2 becomes 3.32%
15
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 16 -->

Figure 9: Diurnal eﬀects in the price impact coeﬃcient ˆβi, the average depth Di and the param-
eters ˆci, ˆλi. Most of the intraday variation in price impact coeﬃcients comes from variations in
depth, while parameters ˆci, ˆλi are relatively more stable.
higher than on average. Moreover, price impact coeﬃcients between 9:30 and 10am are ﬁve
times higher than between 3:30 and 4pm.
The intraday pattern in price impact can be used to explain intraday patterns in price
volatility, observed by many studies ([1], [5], [21], [38]). Similarly to the price impact coeﬃcient
and the market depth, we computed the intraday patterns in variances of ∆Pk,i and OFIk,i,
using our half-hour subsamples. Taking the variance on both sides in equation (7), we obtain a
link between var[∆Pk,i], var[OFIk,i] and βi:
var[∆Pk,i] = β2
i var[OFIk,i] + var[ϵk,i]
(20)
The average variance patterns are plotted on Figure 10. Notice that price volatility has
a sharp peak near the market open, while volatility of OFI peaks near the market close. The
latter peak is oﬀset by low price impact, which gradually declined throughout the day. For the
i-th half-hour interval, equation (20) implies that var[∆Pk,i] ≈ˆβ2
i var[OFIk,i] because var[ϵk,i]
is relatively small, which is also demonstrated16 on Figure 10. Since the R2 in regression (14) is
high, the ratio
var[ϵk,i]
var[OFIk,i] is small, and we can rewrite (20) as βi ≈σP,i
σO,i , where σP,i =
p
var[∆Pk,i]
and σO,i =
p
var[OFIk,i]. This bears strong resemblance to the deﬁnition of Kyle’s λ (see [33]) -
a metric that is used in the asset pricing literature to gauge liquidity risk (see [4] and references
therein).
This metric is traditionally estimated as a slope βL
i
in regression (16a), but our
analysis suggests that βi is a better estimate. Although one could also write βL
i ≈σP,i
σT,i , where
σT,i =
p
var[TIk,i], this would be a poorer approximation because
var[ηk,i]
var[TIk,i] >
var[ϵk,i]
var[OFIk,i] as
shown by R2 values in Table 3.
The intraday pattern in price variance was explained in an earlier study [38] using a struc-
tural model. The authors argued that price volatility is higher in the morning because of a
higher inﬂow of public and private information.
In another study [21] the morning peak of
price volatility is explained mostly by higher intensity of public information. Both studies agree
that the impact of trades is larger in the morning. Our model contributes to this discussion
by explaining the peak of price volatility using tangible quantities, rather than unobservable
information variables. Our ﬁndings also suggest that price impact and information asymmetry
16 ˆβ2
i var[OFIk,i] was computed from the average patterns of ˆβi and var[OFIk,i]
16
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 17 -->

Figure 10: Diurnal variability in variances var[∆Pk,i], var[OFIk,i], the price impact coeﬃcient
ˆβi and the expression β2
i var[OFIk]i.
may be, in fact, two sides of the same coin. If there is more private information in the morning
than in the evening and if limit order traders are aware of this information asymmetry, their
participation will likely diminish in the morning, leading to lower depth near market open. At
the same time, low depth implies a higher price impact in our model, making the information
advantages harder to realize at the market open.
4.3
Volume and volatility
The positive correlation between magnitudes of price changes and trading volume is empirically
conﬁrmed by many authors (see [29] for a review). Recently, trading volume became an impor-
tant metric for order execution algorithms - these algorithms often attempt to match a certain
percentage of the total traded volume to reduce the price impact. However, it remains unclear
whether trading volume truly determines the magnitude of price moves and whether it is a good
metric for price impact. Casting doubt on this assertion, it was found in [28] that the relation
between daily volatility and daily volume is essentially due to the number of trades and not the
volume per se (also see [10] for a following discussion).
We provide further evidence that volume is not a driver of price volatility, now on intraday
timescales. First, we prove that even when prices are purely driven by OFI and not by volume,
a concave relation between magnitude of price changes and transaction volume emerges as an
artifact due to aggregation of data across time. Second, we conﬁrm that such relation exists in
the data, but it becomes statistically insigniﬁcant after accounting for magnitude of OFI.
Comparing the deﬁnitions of V OL and OFI we note that both quantities are sums of
random variables. As the aggregation time window [tk−1, tk] becomes progressively larger, the
behavior of these sums (under certain assumptions) will be governed by the Law of Large
Numbers and the Central Limit Theorem. We consider a general time interval [0, T] and denote
by N(T) the number of order book events during that time interval. We also denote by OFI(T)
17
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 18 -->

and V OL(T), respectively, the order ﬂow imbalance and the traded volume during [0, T]. The
following proposition shows a link between OFI(T) and V OL(T) as T grows.
Proposition 1 Assume that
1.
N(T)
T
→Λ, as T →∞, where Λ is the average arrival rate of order book events.
2. {ei}i≥1 form a covariance-stationary sequence and have a linear-process representation
ei =
∞
P
j=0
ajYi−j, where Yi is a two-sided sequence of i.i.d random variables with E[Yi] = 0
and E[Y 2
i ] = 1, and aj is a sequence of constants with
∞
P
j=0
a2
j = σ2 < ∞.
Moreover,
cov(e1, e1+n) ∼cn2(H−1) as n →∞, where 0 < H < 1 is a constant that governs the decay
of the autocorrelation function.
3. {wi}i≥1, wi = bi +si are random variables with a ﬁnite mean µπ, where π is the proportion
of order book events that correspond to trades and µ is the mean trade size. E|wi|p < ∞
for some p > 1 and P
N≥1
1
N (E| 1
N
P
i≤N
wi|q)r/q < ∞for some r, q such that 0 < r ≤q ≤∞
and r/q ≤1 −1/p.
Then
(µπ)H
σ
OFI(T)
V OLH(T)
T→∞
⇒ξ ∼N(0, 1)
where ⇒denotes convergence in distribution.
The proof of this Proposition is given in the appendix. If the time interval [0, T] includes a large
enough number of order book events, Proposition 1 implies that
OFI(T) ∼ξ
σ
(µπ)H V OLH(T) ≃N

0,
σ2
(µπ)2H V OL2H(T)

(21)
If the time intervals [tk−1,i, tk,i] are large enough to support this approximation then substituting
(21) in (7) yields
∆Pk,i ∼N

0, σ2β2
i
(µπ)2H V OL2H
k,i + σi

where σi = var[ϵk,i]. Note that even if σi = 0, i.e. even if volume cannot aﬀect price volatility
through the residual variance, Proposition 1 predicts a spurious relation between price volatility
and volume.
Interestingly, the recent theory of market microstructure invariants (see [34]) also predicts
a relation between the volatility of order ﬂow imbalance and trading volume. In their analysis,
order ﬂow imbalance is deﬁned diﬀerently based on unobservable “bets”, however it is natural
to assume positive correlation between OFI and the imbalance of “bets”, since the latter reach
exchanges in form of actual orders.
We can recast this statement in a testable form for the magnitudes (absolute values) of
price changes. Assuming ϵk,i ≈0, the scaling argument in Proposition 1 together with our linear
price impact model imply that
|OFIk,i| ≈
σ
(µπ)H V OLH
k,i|ξk,i|
(22)
|∆Pk,i| ≈
βiσ
(µπ)H V OLH
k,i|ξk,i|
(23)
We denote by θi =
βiσ
(µπ)H and take logarithms in (23) to obtain
18
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 19 -->

log |∆Pk,i| = log ˆθi + ˆHi log V OLk,i + log |ˆξk,i|
(24)
Based on Proposition 1, we expect this relation to be indirect (i.e. come through |OFIk,i|)
and noisy. To conﬁrm this empirically, we estimate three regressions17:
|∆Pk,i| = ˆαO
i + ˆβO
i |OFIk,i| + ˆϵO
k,i
(25a)
|∆Pk,i| = ˆαV
i + ˆβV
i V OL
ˆHi
k,i + ˆϵV
k,i
(25b)
|∆Pk,i| = ˆαW
i
+ ˆφO
i |OFIk,i| + ˆφV
i V OL
ˆHi
k,i + ˆϵW
k,i
(25c)
These regressions are estimated for every half-hour subsample with the exponents ˆHi pre-
estimated by (24). The averages of ˆHi and their standard deviation for each stock are presented
on the left panel in Table 5. The exponent varies considerably across stocks and time, but is
generally below 1/2 in our data. The average results of regressions (25a-25c) for each stock are
presented on the middle and right panels. We observe that |OFIk,i| explains the magnitude of
price moves better than V OL
ˆHi
k,i. Although both variables appear to be statistically signiﬁcant
when taken individually, the t-statistics for V OLk,i drop to marginally signiﬁcant levels in the
multiple regression. Thus, the dependence between absolute values of price moves and traded
volume seems to come mostly from correlation between V OLk,i and |OFIk,i|. Interestingly, the
number of trades variable (suggested in [28]) is also statistically signiﬁcant on a stand-alone
basis, but becomes insigniﬁcant when added to (25c) as a third variable. Given the recent pro-
liferation of order splitting, the size of most orders is equal to one lot, so V OLk,i is almost the
same as the number of trades variable.
5
Conclusion
We have introduced order ﬂow imbalance, a variable that cumulates the sizes of order book
events, treating the contributions of market, limit and cancel orders equally, and provided em-
pirical and theoretical evidence for a linear relation between high-frequency price changes and
order ﬂow imbalance for individual stocks. We have shown that this linear model is robust
across stocks and timescales, and the price impact coeﬃcient is inversely proportional to market
depth. These relations suggest that prices respond to changes in the supply and demand for
shares at the best quotes, and that the impact coeﬃcient ﬂuctuates with the amount of liquidity
provision, or depth, in the market. Moreover, we have demonstrated that order ﬂow imbalance
is a more general metric of supply/demand dynamics than trade imbalance, and it can be used
to analyze intraday changes in volatility, and monitor possible adverse selection in limit order
executions. Trades seem to carry little to no information about price changes after the simulta-
neous order ﬂow imbalance is taken into account. If trades do not help to explain price changes
after controlling for the order ﬂow imbalance, it is highly possible that the relation between
the magnitude of price changes, or price volatility and traded volume simply captures the noisy
scaling relation between these variables.
17Here we estimate linear regressions rather than log-linear ones to directly test whether the eﬀect of V OL is
consumed by |OFI| variable
19
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 20 -->

References
[1] H. Ahn, K. Bae, and K. Chan, Limit orders, depth, and volatility: evidence from the
stock exchange of Hong Kong, Journal of Finance, 56 (2001), pp. 767–788.
[2] R. Almgren and N. Chriss, Optimal execution of portfolio transactions, Journal of Risk,
3 (2000), pp. 5–39.
[3] R. Almgren, C. Thum, E. Hauptmann, and H. Li, Direct estimation of equity market
impact, Risk, 18 (2005), p. 57.
[4] Y. Amihud, H. Mendelson, and L. H. Pedersen, Liquidity and Asset Prices, Founa-
tions and Trends in Finance, 1 (2006), pp. 269–364.
[5] T. Andersen and T. Bollerslev, Deutsche mark - dollar volatility: intraday activity
patterns, macroeconomic announcements, and longer run dependencies, Journal of Finance,
53 (1998), p. 219.
[6] M. Avellaneda, S. Stoikov, and J. Reed, Forecasting prices from level-I quotes in the
presence of hidden liquidity. Working paper, 2010.
[7] D. Bertsimas and A. Lo, Optimal control of execution costs, Journal of Financial Mar-
kets, 1 (1998), pp. 1–50.
[8] J.-P. Bouchaud, Price Impact, Wiley, 2010.
[9] J.-P. Bouchaud, Y. Gefen, M. Potters, and M. Wyart, Fluctuations and response
in ﬁnancial markets: the subtle nature of ’random’ price changes, Quantitative Finance, 4
(2004), p. 176.
[10] K. L. Chan and W.-M. Fong, Trade Size, Order Imbalance, and the Volatility-Volume
Relation, Journal of Financial Economics, 57 (2000), pp. 247–273.
[11] T. Chordia, R. Roll, and A. Subrahmanyam, Liquidity and market eﬃciency, Journal
of Financial Economics, 87 (2008), p. 249.
[12] Z. Eisler, J.-P. Bouchaud, and J. Kockelkoren, The price impact of order
book events: market orders, limit orders and cancellations, Quantitative Finance Papers
0904.0900, arXiv.org, Apr. 2009.
[13] P. Embrechts, C. Kluppelberg, and T. Mikosch, Modelling extremal events for
insurance and ﬁnance, Springer, 1997.
[14] R. Engle, R. Ferstenberg, and J. Russel, Measuring and modeling execution cost
and risk. NYU Working Paper No. FIN-06-044, 2006.
[15] R. Engle and A. Lunde, Trades and quotes: a bivariate point process, Journal of Finan-
cial Econometrics, 1 (2003), pp. 159–188.
[16] M. Evans and R. Lyons, Order ﬂow and exchange rate dynamics, Journal of Political
Economy, 110 (2002), p. 170.
[17] J. D. Farmer, L. Gillemot, F. Lillo, S. Mike, and A. Sen, What really causes large
price changes?, Quantitative Finance, 4 (2004), pp. 383–397.
[18] X. Gabaix, P. Gopikrishnan, V. Plerou, and H. Stanley, A theory of power-law
distributions in ﬁnancial market ﬂuctuations, Nature, 423 (2003), p. 267.
20
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 21 -->

[19] J. Gatheral, No-dynamic-arbitrage and market impact, Quantitative Finance, 10 (2010),
p. 749.
[20] J. Hasbrouck, Measuring the information content of stock trades, Journal of Finance, 46
(1991), pp. 179–207.
[21]
, The summary informativeness of stock trades: An econometric analysis, Review of
Financial Studies, 4 (1991), p. 571.
[22] J. Hasbrouck, The Best Bid and Oﬀer: A Short Note on Programs and Practices. 2010.
[23] J. Hasbrouck and G. Saar, Low-latency trading. 2010.
[24] J. Hasbrouck and D. Seppi, Common factors in prices, order ﬂows and liquidity, Journal
of Finance and Economics, 59 (2001), p. 383.
[25] N. Hautsch and R. Huang, The market impact of a limit order. SFB 649 Discussion
Papers, 2009.
[26] C. Hopman, Do supply and demand drive stock prices?, Quantitative Finance, 7 (2007),
pp. 37–53.
[27] G. Huberman and W. Stanzl, Price manipulation and quasi-arbitrage, Econometrica,
72 (2004), pp. 1247–1275.
[28] C. Jones, G. Kaul, and M. Lipson, Transactions, volume, and volatility, Review of
Financial Studies, 7 (1994), pp. 631–651.
[29] J. Karpoff, The relation between price changes and trading volume: A survey, Journal of
Financial and Quantitative Analysis, 22 (1987), p. 109.
[30] D. Keim and A. Madhavan, The upstairs market for large-block transactions: Analysis
and measurement of price eﬀects, Review of Economic Studies, 9 (1996), p. 1.
[31] A. Kempf and O. Korn, Market depth and order size, Journal of Financial Markets, 2
(1999), p. 29.
[32] P. Knez and M. Ready, Estimating the proﬁts from trading strategies, Review of Financial
Studies, 9 (1996), p. 1121.
[33] A. Kyle, Continuous auctions and insider trading, Econometrica, 53 (1985), p. 1315.
[34] A. S. Kyle and A. A. Obizhaeva, Market Microstructure Invariants : Theory and
Implications of Calibration. 2011.
[35] C. Lee, B. Mucklow, and M. Ready, Spreads, depths, and the impact of earnings
information: an intraday analysis, Review of Financial Studies, 6 (1993), pp. 345–374.
[36] C. Lee and M. Ready, Inferring trade direction from intraday data, Journal of Finance,
46 (1991), pp. 733–746.
[37] R. Lyons, Strong laws of large numbers for weakly correlated random variables., Michigan
Mathematical Journal, 35 (1988), pp. 353–359.
[38] A. Madhavan, M. Richardson, and M. Roomans, Why do security prices change? a
transaction-level analysis of nyse stocks, Review of Financial Studies, 10 (1997), p. 1035.
21
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 22 -->

[39] T. McInish and R. Wood, An analysis of intraday patterns in bid/ask spreads for nyse
stocks, Journal of Finance, 47 (1992), pp. 753–764.
[40] A. Obizhaeva and J. Wang, Optimal trading strategy and supply/demand dynamics.
NBER Working Papers, No 11444, 2005.
[41] E. Odders-White, On the occurrence and consequences of inaccurate trade classiﬁcation,
Journal of Financial Markets, 3 (2000), pp. 259–286.
[42] V. Plerou, P. Gopikrishnan, X. Gabaix, and H. Stanley, Quantifying stock-price
response to demand ﬂuctuations, Physical Review E, 66 (2002), p. 027104.
[43] M. Potters and J. Bouchaud, More statistical properties of order books and price
impact, Physica A, 324 (2003), p. 133 140.
[44] S. Predoiu, G. Shaikhet, and S. Shreve, Optimal Execution in a General One-Sided
Limit Order Book. 2010.
[45] I. Rosu, A dynamic model of the limit order book, Review of Financial Studies, 22 (2009),
p. 4601.
[46] C. Stephens, H. Waelbroeck, and A. Mendoza, Relating market impact to aggregate
order ﬂow: the role of supply and demand in explaining concavity and order ﬂow dynamics.
Working Paper Series, 11 2009.
[47] E. Theissen, A test of the accuracy of the lee/ready trade classiﬁcation algorithm, Journal
of International Financial Markets, Institutions and Money, 11 (2001), pp. 147–165.
[48] N. Torre and M. Ferrari, The Market Impact Model, BARRA, 1997.
[49] P. Weber and B. Rosenow, Order book approach to price impact, Quantitative Finance,
5 (2005), pp. 357–364.
[50] P. Weber and B. Rosenow, Large stock price changes: volume or liquidity?, Quantitative
Finance, 6 (2006), p. 7.
[51] W. Whitt, Stochastic-Process Limits, Springer, 2002.
[52] I. Zovko and J. D. Farmer, The power of patience: A behavioral regularity in limit order
placement, Quantitative Finance, 2 (2002), pp. 387–392.
22
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 23 -->

A
Appendix: TAQ data processing
We considered only quotes with timestamps ∈[9:30 am, 4:00 pm], positive bid/ask prices and
sizes and quote mode ̸∈{4, 7, 9, 11, 13, 14, 15, 19, 20, 27, 28}. Similarly, trades were considered
only if they had timestamps ∈[9:30 am, 4:00 pm], positive price and size, correction indica-
tor ≤2 and condition ̸∈{”O”, ”Z”, ”B”, ”T”, ”L”, ”G”, ”W”, ”J”, ”K”}.
From the ﬁltered quotes data we construct the National Best Bid and Oﬀer (NBBO) quotes.
This is done by scanning through the ﬁltered quotes data, while maintaining a matrix with the
best quotes for every exchange. When a new entry is read, we check the exchange ﬂag of that
entry and update the corresponding row in the exchange matrix. Using this matrix, the NBBO
prices are computed at each entry as the highest bid and the lowest ask across all exchanges.
The NBBO sizes are simply the sums of all sizes at the NBBO bid and ask across all exchanges.
For more details on TAQ dataset we refer the reader to [22], which discusses some particularities
of that data, such as possible mis-sequencing of data across exchanges and lack of odd-lot sized
orders. With our auxilary dataset we checked that neither of these issues signiﬁcantly aﬀects
our results.
After the NBBO quotes are computed, we applied a simple quote test to the NBBO quotes
and the ﬁltered trades data. This test matches trades with NBBO quotes and computes the
direction of matched trades. A trade is matched with a quote, if:
1. Trade is not inside the spread, i.e.
(a) Trade price ≥NBBO ask: in this case the trade is considered to be a buy trade.
(b) Trade price ≤NBBO bid: in this case the trade is considered to be a sell trade.
2. Trade date = quote date.
3. Trade timestamp ∈[quote timestamp, quote timestamp + 1 second].
4. If the above conditions allow to match a trade with several quotes, it is matched with the
earliest quote.
This matching algoritm cannot identify the direction of trades occuring within the bid-ask
spread. By comparing the number of matched trades with the overall number of trades in our
sample, we found that 59-95% of trades depending on the stock cannot be matched. Although
these percentages appear to be extremely large, the volume percentage of unmatched trades is
only 10-39% depending on the stock with an average of 17% across stocks, and we believe that
omitting these trades does not aﬀect our results. There are other routines to estimate trade
direction, including the tick test and the Lee-Ready rule [36]. Although the latter is used quite
frequently, there seems to be no compelling evidence of superiority of either of these heuristics
[41, 47]. To test the robustness of our ﬁndings to the choice of a trade direction test, we compared
our results on a subsample of stocks, applying alternatively the tick test or our quote test and
results were virtually the same.
Finally, we removed observations with high bid-ask spreads to ﬁlter out “stub quotes” and
data errors. To apply this ﬁlter coherently across stocks, we computed the 95-th percentile of bid-
ask spread distribution for each stock and removed 5% of that stock’s quotes with spreads above
that percentile. For the representative stock in our sample (SLB), the removed observations fall
mostly on the ﬁrst minutes after market opening: 15.8% of them occur between 9:30 am and
9:35 am, and 42.1% of them occur between 9:30 am and 10:00 am. The average bid-ask spread
of the removed quotes is 3.44 cents with a standard deviation 11.98 cents, the average queue
size of these quotes is 11.78 round lots with a standard deviation 12.89 lots. The average time
interval between two removed quotes is 1.03 seconds with a standard deviation 41.64 seconds.
All of the results and tables in this paper are generated using the ﬁltered data.
23
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 24 -->

B
Appendix: Robustness checks
B.1
Cross-sectional evidence
Table 1. Descriptive statistics
Name
Ticker
Price
Daily
Number of
Number of
Average
Maximum
Best quote
volume,
best quote
trades
Spread,
spread,
size,
round lots
updates
cents
cents
round lots
Advanced Micro Devices
AMD
9.61
20872996
417204
6687
1
1
1035
Apollo Group
APOL
62.92
1949337
172942
4095
2
5
15
American Express
AXP
45.21
8678723
559701
7748
1
24
79
Autozone
AZO
179.03
243197
43682
1081
9
35
7
Bank of America
BAC
18.43
164550168
1529395
15008
1
1
3208
Becton Dickinson
BDX
78.07
1130362
61029
2968
2
5
15
Bank of New York Mellon
BK
31.77
6310701
285619
5518
1
1
122
Boston Scientiﬁc
BSX
7.13
25746787
309441
6768
1
1
2965
Peabody Energy corp
BTU
47.14
5210642
298616
7267
1
3
29
Caterpillar
CAT
67.20
6664891
392499
8224
1
2
38
Chubb
CB
52.22
1951618
149010
3601
1
2
43
Carnival
CCL
40.16
4275911
215427
5503
1
2
53
Cincinnati Financial
CINF
29.41
688914
51373
1528
1
2
42
CME Group
CME
322.83
418955
38504
1412
31
103
5
Coach
COH
41.91
3126469
176795
4458
1
2
41
ConocoPhillips
COP
56.09
9644544
426614
8621
1
2
84
Coventry Health Care
CVH
24.16
1157022
79305
2213
1
2
38
Denbury Resources
DNR
17.88
5737740
263173
4643
1
1
186
Devon Energy
DVN
66.98
3260982
177006
5805
2
4
18
Equifax
EFX
35.34
799505
62957
1945
1
3
39
Eaton
ETN
78.53
1757136
67989
3580
2
6
13
Fiserv
FISV
52.56
1038311
58304
2208
1
3
20
Hasbro
HAS
39.48
1322037
86040
2672
1
2
34
HCP
HCP
32.63
2872521
213045
4357
1
2
48
Starwood Hotels
HOT
50.59
3164807
150252
5106
2
4
22
Kohl’s
KSS
56.88
3064821
128196
4936
1
3
27
L-3 Communications
LLL
94.64
670937
72818
2141
2
6
9
Lockheed Martin
LMT
84.14
1416072
88254
3333
2
5
15
Macy’s
M
23.40
8324639
491756
6469
1
1
176
Marriott
MAR
34.45
5014098
238190
5499
1
2
65
McAfee
MFE
40.04
2469324
109073
3561
1
2
40
McGraw-Hill
MHP
34.90
1954576
102389
3261
1
2
42
Medco Health Solutions
MHS
63.22
2798098
109382
4680
1
3
25
Merck
MRK
36.03
13930842
448748
7997
1
1
231
Marathon Oil
MRO
32.33
5035354
341408
5522
1
1
143
MeadWestvaco
MWV
26.96
1035547
92825
2312
1
3
37
Newmont Mining
NEM
53.43
5673718
435295
7717
1
2
38
Omnicom
OMC
41.17
3357585
150800
4359
1
2
65
MetroPCS Communications
PCS
7.53
4424560
107967
2901
1
1
523
Pultegroup
PHM
11.80
6834683
262420
4604
1
1
319
PerkinElmer
PKI
23.98
1268774
78114
2127
1
2
72
Ryder System
R
44.01
631889
47422
2085
2
5
11
Reynolds American
RAI
54.44
773387
56236
2076
1
4
22
Schlumberger
SLB
67.94
9476060
440839
10286
1
2
39
Teco Energy
TE
16.52
1070815
70318
1807
1
1
148
Time Warner Cable
TWC
53.21
1770234
88286
3554
2
3
22
Whirlpool
WHR
97.73
1424264
134152
3348
4
9
10
Windstream
WIN
11.03
2508830
104887
2937
1
1
798
Watson Pharmaceuticals
WPI
42.51
895967
63094
2024
1
3
29
XTO Energy
XTO
48.13
7219436
612804
5040
1
7
225
Grand mean
51.75
7512376
223232
4552
2
6
227
Table 1 presents the average mid-price, daily transaction volume, daily number of best
quote updates, daily number of trades, spread and the depth at the best bid and ask for 50
randomly chosen U.S. stocks. One round lot is equal to 100 shares. All values are calculated
from the ﬁltered data, that consists of 21 trading day during April, 2010.
24
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 25 -->

Table 2. Relation between price changes and order ﬂow imbalance.
Ticker
Average results
Hypothesis testing
ˆα
t(ˆα)
ˆβi
t(ˆβi)
ˆγQ
i
t(ˆγQ
i )
R2
{αi ̸= 0}
{βi ̸= 0}
{γQ
i
̸= 0}
AMD
-0.0032
-0.24
0.0008
11.10
1.4E-07
0.93
64%
0%
100%
36%
APOL
0.0038
0.13
0.0555
10.74
-2.2E-04
-2.42
63%
17%
96%
6%
AXP
0.0019
0.11
0.0082
14.12
-3.8E-06
-1.37
69%
16%
100%
8%
AZO
0.0101
0.34
0.1619
7.02
-9.3E-04
-1.40
47%
25%
99%
6%
BAC
-0.0018
-0.13
0.0002
19.08
1.9E-09
-0.08
79%
3%
100%
14%
BDX
-0.0008
-0.07
0.0536
10.77
-1.1E-04
-0.74
63%
12%
100%
12%
BK
-0.0078
-0.26
0.0069
15.56
-4.0E-06
-0.89
74%
6%
100%
8%
BSX
0.0000
0.01
0.0003
7.55
7.8E-08
3.51
58%
3%
88%
51%
BTU
0.0048
0.15
0.0242
14.75
-3.5E-05
-2.05
72%
16%
100%
3%
CAT
0.0147
0.30
0.0194
14.80
-1.9E-05
-1.72
71%
19%
100%
5%
CB
-0.0086
-0.05
0.0191
12.61
-3.5E-07
-0.04
64%
10%
100%
18%
CCL
-0.0067
-0.24
0.0140
14.16
-1.2E-05
-1.03
70%
7%
100%
11%
CINF
-0.0030
-0.02
0.0260
11.66
-7.0E-06
0.38
70%
4%
99%
30%
CME
0.0506
0.06
0.6262
5.46
-7.2E-03
-1.66
35%
18%
96%
7%
COH
-0.0221
-0.54
0.0179
13.13
-1.7E-05
-1.18
69%
5%
100%
7%
COP
-0.0008
0.10
0.0084
12.79
-5.8E-06
-1.86
68%
13%
100%
5%
CVH
-0.0034
-0.07
0.0217
11.74
7.6E-06
0.37
65%
7%
99%
20%
DNR
-0.0008
-0.07
0.0045
13.78
-1.3E-07
0.19
69%
5%
99%
22%
DVN
0.0112
0.20
0.0370
12.11
-1.0E-04
-2.72
65%
19%
100%
2%
EFX
-0.0032
-0.06
0.0222
9.47
6.4E-05
0.87
56%
6%
99%
32%
ETN
-0.0076
0.10
0.0712
11.01
-2.3E-04
-1.81
65%
17%
100%
4%
FISV
-0.0002
0.10
0.0397
11.09
-2.3E-05
-0.28
63%
10%
100%
16%
HAS
-0.0031
-0.01
0.0222
12.36
4.7E-06
0.28
67%
6%
100%
23%
HCP
-0.0078
-0.21
0.0150
13.82
-1.4E-05
-0.63
67%
5%
100%
10%
HOT
-0.0012
0.05
0.0345
12.94
-7.2E-05
-2.06
68%
14%
100%
4%
KSS
-0.0030
-0.05
0.0317
14.10
-5.4E-05
-1.38
71%
13%
100%
5%
LLL
0.0160
0.42
0.1000
12.34
-3.8E-04
-1.56
67%
22%
98%
7%
LMT
0.0006
0.00
0.0520
14.14
-1.2E-04
-1.49
72%
17%
100%
4%
M
-0.0010
0.07
0.0043
16.61
8.8E-08
0.15
75%
6%
100%
19%
MAR
-0.0039
0.02
0.0121
15.10
-4.1E-06
-0.43
71%
10%
100%
10%
MFE
0.0087
0.22
0.0205
13.19
-3.8E-05
-0.63
68%
11%
100%
11%
MHP
-0.0073
-0.18
0.0211
12.41
5.8E-06
0.18
68%
5%
99%
24%
MHS
-0.0055
-0.20
0.0334
11.97
-8.3E-05
-1.64
66%
12%
100%
4%
MRK
-0.0065
-0.26
0.0032
13.26
-5.4E-07
-0.61
69%
4%
100%
14%
MRO
0.0018
0.12
0.0058
14.16
-3.6E-07
0.32
69%
8%
100%
23%
MWV
-0.0011
0.02
0.0205
12.55
-1.7E-05
-0.31
68%
9%
100%
17%
NEM
-0.0102
-0.26
0.0170
13.90
-1.9E-05
-2.15
71%
12%
100%
5%
OMC
-0.0099
-0.36
0.0144
12.40
-4.5E-06
-0.19
65%
4%
100%
20%
PCS
-0.0006
-0.05
0.0015
6.52
1.8E-06
3.79
53%
2%
86%
51%
PHM
0.0006
0.02
0.0027
11.27
8.4E-07
1.20
66%
3%
99%
36%
PKI
-0.0004
-0.05
0.0102
7.96
4.1E-05
2.15
53%
3%
96%
51%
R
0.0006
0.03
0.0667
10.90
3.7E-05
-0.21
63%
14%
100%
16%
RAI
-0.0070
-0.10
0.0396
11.39
2.6E-05
-0.03
66%
9%
100%
19%
SLB
-0.0077
-0.21
0.0198
16.27
-1.8E-05
-1.67
76%
10%
100%
2%
TE
0.0011
0.05
0.0049
7.76
1.4E-05
3.27
54%
4%
91%
55%
TWC
-0.0130
-0.15
0.0384
12.24
-5.6E-05
-0.73
64%
12%
99%
9%
WHR
0.0628
0.73
0.1278
11.10
-3.3E-04
-1.44
65%
25%
100%
7%
WIN
-0.0004
-0.04
0.0009
4.32
1.5E-06
3.98
44%
1%
72%
43%
WPI
-0.0090
-0.27
0.0270
11.46
2.9E-05
0.26
66%
5%
99%
23%
XTO
-0.0088
-0.25
0.0029
13.26
2.7E-07
0.48
65%
3%
100%
28%
Average
0.0002
-0.02
0.0398
12.08
-2.0E-04
-0.32
65%
10%
98%
17%
Table 2 presents a cross-section of results (averaged across time) for regressions:
∆Pk,i = ˆαi + ˆβiOFIk,i + ˆϵk,i,
∆Pk,i = ˆαQ
i + ˆβQ
i OFIk,i + ˆγQ
i OFIk,i|OFIk,i| + ˆϵQ
k,i,
where ∆Pk,i are the 10-second mid-price changes in ticks and OFIk,i are the contemporaneous order ﬂow imbalances.
These regressions were estimated using 273 half-hour subsamples (indexed by i) for each stock and their outputs were
averaged across subsamples. Each subsample typically contains about 180 observations (indexed by k). The t-statistics
were computed using Newey-West standard errors. For brevity, we report the R2, the average ˆαi and the average ˆβi only
for the ﬁrst regression (with a single OFIk,i term). There is almost no diﬀerence between averages of estimates ˆβi and ˆβQ
i
and the R2 in two regressions. The last three columns report the percentage of samples where the coeﬃcient(s) passed the
z-test at the 5% signiﬁcance level.
25
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 26 -->

Table 3. Comparison of order ﬂow imbalance and trade imbalance.
Ticker
Order ﬂow imbalance
Trade imbalance
Both covariates
R2
t(ˆβi)
{βi ̸= 0}
F
R2
t(ˆβT
i )
{βT
i ̸= 0}
F
R2
t(ˆθO
i )
t(ˆθT
i )
{θO
i ̸= 0}
{θT
i ̸= 0}
F
AMD
64%
11.10
100%
382
39%
5.06
95%
140
67%
7.64
1.59
99%
45%
214
APOL
63%
10.74
96%
396
30%
5.04
95%
83
66%
8.95
1.58
96%
44%
211
AXP
69%
14.12
100%
449
34%
5.55
92%
101
71%
11.31
1.90
100%
55%
241
AZO
47%
7.02
99%
179
30%
4.88
96%
87
54%
5.78
2.87
98%
81%
118
BAC
79%
19.08
100%
774
45%
7.03
98%
157
80%
13.55
0.80
99%
25%
397
BDX
63%
10.77
100%
362
28%
4.85
92%
79
65%
8.90
1.53
100%
46%
195
BK
74%
15.56
100%
610
36%
5.36
93%
117
75%
11.90
0.80
100%
26%
313
BSX
58%
7.55
88%
338
31%
3.60
71%
106
62%
5.74
0.88
82%
24%
189
BTU
72%
14.75
100%
527
35%
6.03
97%
103
74%
11.96
1.63
100%
44%
277
CAT
71%
14.80
100%
498
33%
5.75
94%
94
72%
12.14
1.55
100%
46%
262
CB
64%
12.61
100%
378
33%
5.47
95%
102
66%
9.41
1.57
99%
44%
202
CCL
70%
14.16
100%
478
32%
5.31
94%
93
71%
11.44
1.17
100%
37%
247
CINF
70%
11.66
99%
552
39%
5.35
96%
141
72%
8.28
1.28
98%
40%
297
CME
35%
5.46
96%
112
24%
4.31
88%
63
44%
4.73
2.78
96%
71%
78
COH
69%
13.13
100%
457
29%
4.75
93%
80
70%
11.06
1.12
100%
31%
238
COP
68%
12.79
100%
450
35%
5.69
92%
107
70%
10.25
1.76
100%
49%
240
CVH
65%
11.74
99%
418
35%
5.05
93%
114
67%
8.43
1.35
97%
37%
222
DNR
69%
13.78
99%
471
32%
4.89
92%
101
70%
10.43
1.27
99%
37%
246
DVN
65%
12.11
100%
414
33%
5.57
95%
96
68%
9.61
2.12
98%
60%
226
EFX
56%
9.47
99%
289
31%
4.75
89%
101
60%
7.13
2.26
98%
55%
167
ETN
65%
11.01
100%
389
25%
4.43
86%
69
67%
9.85
1.47
99%
43%
209
FISV
63%
11.09
100%
380
28%
4.82
93%
79
65%
9.08
1.25
100%
38%
201
HAS
67%
12.36
100%
427
32%
5.15
95%
97
68%
9.67
1.17
100%
34%
223
HCP
67%
13.82
100%
417
31%
5.07
90%
91
68%
10.92
1.33
100%
42%
217
HOT
68%
12.94
100%
438
27%
4.75
88%
74
70%
11.00
1.48
100%
40%
231
KSS
71%
14.10
100%
525
31%
5.16
93%
91
72%
11.86
1.14
100%
37%
274
LLL
67%
12.34
98%
485
36%
6.00
95%
117
70%
9.68
2.14
98%
57%
270
LMT
72%
14.14
100%
516
35%
5.80
96%
105
73%
11.35
1.83
100%
51%
277
M
75%
16.61
100%
640
35%
5.10
93%
108
76%
12.80
1.13
100%
38%
330
MAR
71%
15.10
100%
498
34%
5.54
95%
105
72%
11.41
1.18
100%
36%
258
MFE
68%
13.19
100%
463
31%
4.82
88%
93
69%
10.27
0.89
100%
30%
239
MHP
68%
12.41
99%
489
31%
5.09
93%
96
70%
9.94
1.04
99%
33%
257
MHS
66%
11.97
100%
414
28%
4.81
89%
80
68%
10.03
1.50
99%
40%
218
MRK
69%
13.26
100%
451
31%
4.99
92%
93
70%
10.41
1.02
100%
29%
235
MRO
69%
14.16
100%
465
35%
5.38
96%
104
70%
10.67
1.12
100%
35%
241
MWV
68%
12.55
100%
452
34%
5.30
96%
102
69%
9.66
1.01
100%
33%
237
NEM
71%
13.90
100%
490
34%
5.77
92%
100
72%
11.38
1.90
100%
54%
260
OMC
65%
12.40
100%
411
30%
4.90
93%
88
67%
9.85
1.22
100%
39%
216
PCS
53%
6.52
86%
297
35%
4.08
74%
169
58%
4.47
1.43
81%
35%
195
PHM
66%
11.27
99%
416
35%
4.76
93%
115
68%
8.40
1.22
98%
38%
224
PKI
53%
7.96
96%
263
28%
3.98
82%
89
57%
6.16
1.70
93%
47%
148
R
63%
10.90
100%
352
27%
4.80
96%
71
65%
9.02
1.58
100%
44%
188
RAI
66%
11.39
100%
422
36%
5.60
98%
111
68%
8.64
1.42
100%
43%
224
SLB
76%
16.27
100%
644
32%
5.31
89%
94
77%
13.91
1.56
100%
47%
336
TE
54%
7.76
91%
301
37%
4.65
82%
175
60%
5.27
1.96
86%
45%
200
TWC
64%
12.24
99%
377
31%
5.21
86%
93
66%
9.67
1.70
99%
45%
201
WHR
65%
11.10
100%
394
29%
5.03
95%
85
67%
9.27
1.86
100%
52%
217
WIN
44%
4.32
72%
243
41%
4.74
75%
249
58%
2.60
2.55
58%
47%
206
WPI
66%
11.46
99%
437
32%
4.80
93%
100
68%
8.95
1.35
99%
46%
232
XTO
65%
13.26
100%
399
21%
3.78
78%
54
66%
11.72
1.42
100%
40%
209
Average
65%
12.08
98%
429
32%
5.08
91%
103
67%
9.53
1.51
97%
43%
231
Table 3 presents the average results of regressions:
∆Pk,i = ˆαi + ˆβiOF Ik,i + ˆϵk,i,
∆Pk,i = ˆαT
i + ˆβT
i T Ik,i + ˆηk,i,
∆Pk,i = ˆαD
i
+ ˆθO
i OF Ik,i + ˆθT
i T Ik,i + ˆϵD
k,i,
where ∆Pk,i are the 10-second mid-price changes, OF Ik,i are the contemporaneous order ﬂow imbalances and T Ik,i are the contemporaneous
trade imbalances.
These regressions were estimated using 273 half-hour subsamples (indexed by i) for each stock and their outputs were
averaged across subsamples. Each subsample typically contains about 180 observations (indexed by k). The t-statistics were computed using
Newey-West standard errors. For each of three regressions, Table 3 reports the average R2, the average t-statistic of the coeﬃcient(s), the
percentage of samples where the coeﬃcient(s) passed the z-test at the 5% signiﬁcance level and the F-statistic of the regression.
26
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 27 -->

Table 4. Relation between the price impact coeﬃcient and market depth.
Ticker
Parameter estimates
Fit measures
ˆc
ˆλ
t(ˆc = 0)
t(ˆc = 0.5)
t(ˆλ = 0)
t(ˆλ = 1)
R2
corr[ˆβ, ˆˆβ]2
corr[ˆβ, ˆˆβ∗]2
AMD
0.53
1.04
31.06
2.0
22.5
1.0
78%
86%
86%
APOL
0.30
0.38
4.59
-3.2
1.1
-1.8
3%
34%
35%
AXP
0.45
1.01
26.27
-3.2
45.8
0.6
90%
87%
87%
AZO
0.45
0.70
5.47
-0.7
5.2
-2.2
14%
17%
16%
BAC
0.87
1.10
31.80
13.6
19.1
1.7
80%
89%
89%
BDX
0.48
1.03
23.91
-1.2
22.2
0.6
74%
71%
71%
BK
0.47
1.04
28.28
-1.9
68.5
2.5
94%
94%
94%
BSX
0.51
1.02
15.23
0.3
24.1
0.4
73%
81%
81%
BTU
0.58
1.10
45.36
6.2
53.8
5.0
93%
90%
90%
CAT
0.48
1.01
35.12
-1.4
20.7
0.2
91%
91%
90%
CB
0.53
1.09
32.41
2.1
63.6
5.5
93%
91%
91%
CCL
0.45
1.04
35.26
-3.6
41.9
1.5
89%
86%
86%
CINF
0.43
1.03
25.48
-4.2
52.5
1.7
93%
90%
90%
CME
1.21
0.35
2.10
1.2
1.4
-2.7
1%
2%
2%
COH
0.61
1.11
15.35
2.9
44.7
4.3
81%
83%
82%
COP
0.32
0.94
13.77
-8.1
22.6
-1.6
82%
79%
79%
CVH
0.54
1.13
26.92
2.2
37.9
4.2
88%
90%
89%
DNR
0.55
1.10
40.77
3.6
44.9
3.9
92%
90%
90%
DVN
0.34
0.91
16.15
-7.8
19.3
-2.0
48%
61%
61%
EFX
0.43
1.05
19.58
-3.0
27.1
1.2
84%
80%
80%
ETN
0.64
1.11
13.55
2.9
20.8
2.1
65%
63%
63%
FISV
0.47
1.04
25.33
-1.7
34.1
1.3
85%
80%
80%
HAS
0.52
1.08
27.80
1.3
49.8
3.8
90%
86%
85%
HCP
0.37
1.00
33.13
-11.3
64.7
0.0
95%
94%
94%
HOT
0.61
1.13
28.19
5.2
37.7
4.3
87%
87%
87%
KSS
0.59
1.09
28.99
4.3
41.7
3.4
90%
85%
85%
LLL
0.57
1.02
15.30
1.9
14.5
0.3
53%
65%
65%
LMT
0.72
1.17
7.93
2.4
15.6
2.3
69%
63%
63%
M
0.52
1.06
24.92
1.0
52.1
3.0
94%
92%
92%
MAR
0.50
1.06
22.26
0.0
52.7
3.1
92%
89%
89%
MFE
0.47
1.06
22.12
-1.3
45.3
2.7
92%
89%
89%
MHP
0.45
1.02
20.58
-2.1
38.1
0.6
83%
78%
78%
MHS
0.71
1.16
19.88
5.9
39.5
5.3
88%
87%
86%
MRK
0.31
0.94
21.38
-12.8
36.3
-2.3
87%
84%
84%
MRO
0.55
1.09
28.87
2.4
51.9
4.2
94%
94%
94%
MWV
0.54
1.13
28.16
2.2
39.3
4.6
90%
87%
87%
NEM
0.51
1.07
31.09
0.4
39.3
2.6
89%
88%
88%
OMC
0.52
1.04
36.61
1.1
19.5
0.7
86%
90%
90%
PCS
0.43
1.06
22.79
-3.4
18.6
1.1
53%
83%
83%
PHM
0.62
1.10
39.56
7.7
36.6
3.3
87%
92%
92%
PKI
0.49
1.14
29.01
-0.5
34.7
4.4
80%
87%
86%
R
0.50
1.05
17.43
-0.1
15.8
0.7
58%
59%
59%
RAI
0.51
1.07
26.19
0.4
47.3
3.1
88%
79%
79%
SLB
0.56
1.08
23.39
2.5
47.6
3.6
92%
94%
93%
TE
0.35
1.10
12.12
-5.1
25.1
2.2
70%
85%
86%
TWC
0.55
1.07
22.29
1.9
18.9
1.2
73%
85%
84%
WHR
1.09
1.25
12.66
6.9
13.4
2.7
51%
54%
53%
WIN
17.21
1.80
13.95
13.5
12.2
5.4
35%
72%
74%
WPI
0.39
0.99
19.57
-5.6
32.6
-0.4
79%
77%
77%
XTO
0.97
1.19
27.70
13.46
35.64
5.77
88%
91%
90%
Grand mean
0.88
1.05
23.55
0.59
33.40
1.99
76%
79%
79%
Table 4 presents the results of regressions:
log ˆβi =
ˆ
αL,i −ˆλ log Di + ˆϵL,i,
ˆβi =
ˆ
αM,i +
ˆc
Dˆλ
i
+ ˆϵM,i,
where ˆβi is the price impact coeﬃcient for the i-th half-hour subsample and Di is the average market depth for that
subsample. These regressions were estimated for each of the 50 stocks, using 273 estimates of ˆβi for that stock, obtained
from (14). The second regression uses estimates ˆλ obtained from the ﬁrst regression. The t-statistics were computed using
Newey-West standard errors. The last three columns provide three alternative ﬁt measures - the R2 of the linear regression
(17), the squared correlation between ˆβi and ﬁtted values ˆˆβi =
ˆc
Dˆλ
i
and the squared correlation between ˆβi and ˆˆβ∗
i =
ˆc
Di .
27
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 28 -->

Table 5. Comparison of traded volume and order ﬂow imbalance.
Ticker
Avg
Stdev
Order ﬂow imbalance
Traded volume
Both covariates
ˆH
ˆH
R2
t(ˆβO
i )
βO
i ̸= 0
F
R2
t(ˆβV
i )
βV
i
̸= 0
F
R2
t(ˆφO
i )
t(ˆφV
i )
φO
i ̸= 0
φV
i ̸= 0
F
AMD
0.06
0.08
63%
11.7
100%
356
14%
4.6
87%
34
63%
10.8
1.2
99%
38%
182
APOL
0.24
0.08
53%
9.1
97%
258
25%
6.9
100%
63
57%
7.6
3.3
94%
86%
144
AXP
0.16
0.08
55%
11.3
100%
249
20%
6.8
100%
48
57%
9.7
2.9
100%
82%
133
AZO
0.43
0.22
39%
6.3
98%
131
32%
5.8
100%
93
50%
5.0
3.9
97%
98%
98
BAC
0.09
0.08
73%
17.6
100%
560
24%
6.0
89%
61
74%
15.3
1.3
97%
40%
285
BDX
0.26
0.10
55%
9.4
100%
261
27%
6.5
100%
71
58%
7.6
3.1
99%
85%
147
BK
0.11
0.07
68%
14.1
100%
437
19%
6.7
97%
46
68%
12.6
2.0
100%
58%
225
BSX
-0.17
2.41
68%
10.3
100%
486
14%
3.4
97%
33
69%
10.1
0.0
99%
13%
246
BTU
0.24
0.07
58%
11.4
100%
283
23%
7.1
99%
57
60%
9.7
2.6
100%
81%
151
CAT
0.22
0.07
56%
11.0
100%
250
19%
6.3
99%
44
57%
9.7
2.3
100%
68%
131
CB
0.19
0.09
56%
11.1
100%
261
23%
6.5
99%
58
58%
9.1
2.8
100%
76%
141
CCL
0.14
0.07
60%
12.2
100%
309
19%
6.7
99%
45
62%
10.8
2.5
100%
77%
162
CINF
0.13
0.12
67%
12.0
100%
505
30%
6.2
98%
85
69%
10.3
2.1
100%
58%
268
CME
0.49
0.24
28%
4.8
98%
78
30%
5.3
100%
83
42%
3.9
4.1
94%
99%
71
COH
0.19
0.07
60%
11.3
100%
299
22%
6.5
99%
52
61%
9.8
2.4
100%
73%
157
COP
0.16
0.07
56%
10.5
100%
277
20%
6.1
97%
49
58%
9.2
2.5
100%
74%
145
CVH
0.18
0.10
62%
11.4
100%
352
27%
6.1
100%
72
64%
9.2
2.4
100%
73%
189
DNR
0.08
0.07
64%
13.4
100%
376
17%
6.4
95%
38
65%
12.0
1.9
99%
57%
193
DVN
0.26
0.07
52%
9.6
97%
236
24%
6.9
100%
59
55%
8.0
3.2
96%
85%
131
EFX
0.20
0.11
52%
9.1
100%
241
26%
5.6
99%
69
56%
7.3
2.8
99%
77%
137
ETN
0.26
0.10
55%
9.1
99%
252
27%
6.6
99%
70
58%
7.6
3.1
98%
85%
142
FISV
0.19
0.11
57%
10.1
100%
284
25%
6.0
100%
65
59%
8.3
2.4
100%
70%
153
HAS
0.20
0.09
61%
11.3
100%
328
26%
6.3
100%
67
63%
9.5
2.5
100%
76%
175
HCP
0.14
0.07
57%
11.8
100%
268
21%
7.1
99%
50
59%
10.0
2.8
100%
80%
143
HOT
0.23
0.08
57%
10.5
99%
263
24%
7.2
100%
60
60%
9.0
3.2
99%
88%
145
KSS
0.24
0.08
60%
11.6
100%
318
25%
6.8
99%
61
62%
9.8
2.6
99%
78%
169
LLL
0.33
0.12
58%
10.3
97%
323
34%
7.2
100%
101
63%
7.9
3.4
96%
92%
188
LMT
0.28
0.09
61%
11.6
100%
327
31%
7.6
100%
85
64%
9.3
3.1
100%
85%
182
M
0.11
0.07
69%
15.2
100%
463
20%
6.3
100%
46
69%
13.5
2.0
100%
63%
238
MAR
0.15
0.07
61%
13.3
100%
324
21%
7.0
99%
50
62%
11.5
2.5
100%
74%
170
MFE
0.16
0.09
60%
11.7
100%
318
24%
7.0
98%
62
62%
9.7
2.6
100%
73%
170
MHP
0.20
0.10
62%
11.6
100%
377
25%
6.1
100%
62
64%
9.7
2.0
100%
56%
199
MHS
0.23
0.08
56%
10.0
100%
258
24%
6.7
100%
58
58%
8.4
2.9
100%
80%
139
MRK
0.10
0.07
62%
12.1
100%
330
17%
5.5
99%
40
63%
10.8
1.9
100%
60%
170
MRO
0.09
0.06
61%
12.7
100%
333
16%
6.4
97%
36
63%
11.5
2.0
100%
56%
172
MWV
0.18
0.10
62%
11.3
100%
330
28%
6.9
100%
75
64%
9.2
2.6
100%
79%
180
NEM
0.20
0.07
56%
10.6
100%
253
20%
6.3
99%
47
58%
9.3
2.6
100%
79%
135
OMC
0.15
0.09
57%
11.0
100%
286
20%
6.4
98%
48
59%
9.4
2.5
100%
75%
151
PCS
0.11
0.18
62%
8.9
100%
411
18%
3.8
98%
54
63%
8.4
0.8
100%
28%
214
PHM
0.07
0.08
64%
11.5
100%
384
15%
5.4
91%
34
65%
10.7
1.2
100%
41%
195
PKI
0.11
0.11
55%
9.0
99%
266
20%
4.8
98%
47
57%
7.8
1.9
98%
55%
141
R
0.27
0.11
56%
9.8
99%
259
28%
6.3
100%
74
59%
7.9
3.1
99%
87%
147
RAI
0.25
0.10
61%
10.6
100%
334
28%
5.9
99%
73
63%
8.8
2.6
100%
75%
182
SLB
0.24
0.07
62%
12.5
99%
330
19%
5.8
97%
46
63%
11.2
1.9
99%
56%
171
TE
0.09
1.69
60%
9.6
100%
371
18%
4.5
84%
48
61%
8.7
1.3
99%
43%
196
TWC
0.25
0.10
55%
10.5
100%
253
27%
6.8
100%
73
58%
8.4
3.1
99%
83%
142
WHR
0.34
0.11
56%
9.2
99%
272
29%
6.6
100%
78
59%
7.5
3.2
98%
88%
156
WIN
0.06
0.26
48%
5.5
86%
340
10%
2.9
50%
34
49%
5.3
0.6
85%
31%
179
WPI
0.22
0.10
61%
11.0
100%
361
28%
5.9
100%
75
64%
9.0
2.4
99%
71%
196
XTO
0.08
0.06
53%
11.3
100%
238
15%
6.6
100%
32
55%
10.0
2.8
100%
82%
125
Average
0.18
0.18
58%
10.9
99%
313
23%
6.1
97%
58
61%
9.3
2.4
99%
70%
168
Table 5 presents the average results of regressions:
|∆Pk,i| = ˆαO
i + ˆβO
i |OFIk,i| + ˆϵO
k,i,
|∆Pk,i| = ˆαV
i + ˆβV
i V OL
ˆ
Hi
k,i + ˆϵV
k,i,
|∆Pk,i| = ˆαW
i
+ ˆφO
i |OFIk,i| + ˆφV
i V OL
ˆ
Hi
k,i + ˆϵW
k,i,
where ∆Pk,i are the 10-second mid-price changes, OFIk,i are the contemporaneous order ﬂow imbalances and V OLk,i are
the contemporaneous trade volumes. The exponents ˆHi were estimated in each subsample beforehand using a logarithmic
regression: log |∆Pk,i| = log ˆθi + ˆHi log V OLk,i +log |ˆξk,i|. These regressions were estimated using 273 half-hour subsamples
(indexed by i) for each stock and their outputs were averaged across subsamples. Each subsample typically contains about
180 observations (indexed by k). The t-statistics were computed using Newey-West standard errors. For each of three
regressions, Table 5 reports the average R2, the average t-statistic of the coeﬃcient(s), the percentage of samples where the
coeﬃcient(s) passed the z-sest at the 5% signiﬁcance level and the F-statistic of the regression.
28
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 29 -->

B.2
Transaction prices
To reconcile our results with earlier studies that operate in transaction time, we repeated regres-
sions (14,16a,16b) with diﬀerences between transaction prices ∆LP t
k = P t
k −P t
k−L for L trades,
instead of diﬀerences in mid-prices ∆Pk. We picked at random ﬁve stocks from our sample
(BDX, CB, MHS, PHM and PKI), and computed ∆LP t
k for L = 2, 5, 10 trades (we avoided us-
ing L = 1 because of possible issues with trade and quote matching). Using the same inter-trade
time intervals we computed concurrent OFI and TI variables. To ensure that there is an ample
amount of data for each regression, we pooled data across days for each stock and each intraday
time interval, resulting in 13 samples for each stock over a month of data. The results averaged
across time and stocks are presented in Table 6 and closely mirror our results for mid prices.
The variable OFIk explains price changes better than TIk on stand-alone basis. Moreover, the
eﬀect of trades on prices seems to be captured by the order ﬂow imbalance, i.e. the variable TIk
loses its statistical signiﬁcance18. when used together with OFIk in the regression. The increase
in R2 from adding TIk as an extra regressor is almost nill (0.65%, 0.18%, 0.24% for L = 1, 2, 5
respectively).
Interestingly, we found that the relation between trade price changes and OFIk (or TIk) is
sometimes concave. We estimated regressions (14) and (16a) for trade price changes ∆LP t
k with
additional quadratic variable OFIk|OFIk| and found that average t-statistics of its coeﬃcient
are, respectively -3.02, -4.10 and -3.85 for L = 1, 2, 5 trades. The quadratic term is signiﬁcant
at 5% level in 60%, 74% and 85% of samples for respective values of L, and we did not observe
any pattern in these t-statistics, neither across stock nor across time. In the trade imbalance
regression the coeﬃcient near quadratic variable TIk|TIk| is also signiﬁcant with average t-
statistics -3.64, -5.53, -5.48 for respective lag values and it is signiﬁcant in even a larger fraction
of samples.
From these results it appears that price impact is concave when prices are sampled at
trade times, but it is linear when they are sampled at regular time intervals. This eﬀect may
be a consequence of sampling data at special times (i.e. trade times), which may introduce
systematic down biases into the dependent variable. For example, if traders submit large orders
when they expect their impact to be minimal, that would lead to a concave (sublinear) price
impact. Supporting the idea of a sampling bias, we found that when mid-price changes are
sampled at trade times, the price impact of OFIk is again concave in a substantial fraction
of our samples. We also regressed changes in last trade prices sampled regularly at a 1-minute
frequency on OFIk, and observed concave price impact once again. This may again be attributed
to a dependent variable bias - since trades are relatively infrequent, for many time intervals the
trade prices are going to be stale and trade price changes are equal to zero, while mid price
changes are not.
Table 6. Comparison of order ﬂow imbalance and trade imbalance for transaction prices.
Lag
Order ﬂow imbalance
Trade imbalance
Both covariates
R2
t(ˆβi)
{βi ̸= 0}
F
R2
t(ˆβT
i )
{βT
i ̸= 0}
F
R2
t(ˆθO
i )
t(ˆθT
i )
{θO
i ̸= 0}
{θT
i ̸= 0}
F
L = 2 trades
14%
15.03
100%
464
1%
2.97
69%
26
15%
14.19
-2.90
100%
71%
245
L = 5 trades
38%
16.68
98%
753
8%
4.79
88%
113
39%
15.13
-0.14
98%
14%
379
L = 10 trades
51%
14.85
98%
655
13%
4.85
88%
100
51%
13.21
0.70
98%
11%
329
18Here we also use Newey-West standard errors because regression residuals have statistically signiﬁcant auto-
correlation
29
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 30 -->

B.3
Order ﬂow at higher order book levels
The level of detail in our Level 2 auxilary data set allows us to analyze contributions of order
ﬂows at diﬀerent price levels to price formation and to conﬁrm our claim that price changes are
mostly driven by activity at the top of the order book (thus Level 1 data is suﬃcient to study
the impact of limit orders on prices).
For example, consider the bid side of the order book with 10 shares at the top two levels.
Absent any activity on the ask side and the second bid level, an OFI of -11 shares will lead to a
bid price change of -1 tick. However, if 9 orders at the second bid level cancel before that order
ﬂow happens, the same OFI of -11 shares will lead to a price change of -2 ticks. In other words,
if order activity up to second (third, fourth etc) level is important, tracking OFI only at the best
prices will give a ﬂawed picture of price dynamics. To test this assertion, we compute variables
OFIm, m = 2, . . . , 5 from m-th level queue ﬂuctuations similarly to (12) and relabel OFI1 =
OFI. Then we ﬁt ﬁve regressions, similar to (14), where variables OFIm,
m = 2, . . . , 5 are
added one at a time:
∆Pk,i = ˆαM
i
+
M
X
m=1
ˆβm,M
i
OFIm
k,i + ˆϵM
k,i,
M = 1, . . . , 5
(26)
The average results across time for a representative stock are shown on Figure 11. The average
increase in explanatory power (measured by R2) from adding OFI2 as a regressor is 6.22%, which
is quite small compared to the stand-alone R2 of 70.83% for OFI1. The eﬀect of OFI3−OFI5 is
very small, and their coeﬃcients appear to be only marginally signiﬁcant, in contrast with those
of OFI1 and OFI2. The cross-time average of coeﬃcients ˆβ1,1
i
in the simple regression19 with
OFI1 is 0.0597. In the multiple regression with OFI1 and OFI2 the averages of their respective
coeﬃcients are 0.0673 and 0.0406. We conclude that second-level activity, as summarized by
OFI2, has only a second-order inﬂuence on price changes, which are mainly driven by OFI1.
The eﬀect of OFI3 −OFI5 is almost nill.
Figure 11: Cross-time average increase in R2 from inclusion of variables OFI2 −OFI5, and
cross-time average Newey-West t-statistics of their coeﬃcient in the regression with all ﬁve
variables, with NASDAQ ITCH data for the Schlumberger stock (SLB).
19This coeﬃcient is higher than the one obtained with NBBO data, because NASDAQ best quote depth is
smaller than NBBO depth
30
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 31 -->

B.4
Choice of timescale
Using the auxilary Level 2 dataset, we verify that our results are robust to potential issues
in TAQ data, namely odd-lot sized orders at the best bid and oﬀer, and mis-sequencing in
quote data across exchanges during NBBO construction. We also compare our results across
a wide range of timescales. The auxilary data comes from a single exchange (NASDAQ), has
information on orders of all sizes and has timestamps up to a millisecond.
We estimate the regression (14) for a variety of timescales ∆t, ranging from 50 milliseconds
to 5 minutes using separate intraday subsamples as before.
The size of these samples was
diﬀerent in order to stabilize the number of observations per sample. More precisely, data for
the smallest timescales (50, 100 and 500 milliseconds) was separated into 1-minute instead of 30-
minute subsamples to make numerical computations feasible. Data for the largest timescales (30
seconds to 5 minutes) was pooled across days preserving separate 30-minute intraday intervals
to have a large number of observations per sample. The average R2 and Newey-West t-statistics
for OFI across time for each ∆t are presented on Figure 12.
Figure 12: Average R2 and Newey-West t-statistics for OFI coeﬃcient across time for diﬀerent
∆t, with NASDAQ ITCH data for the Schlumberger stock (SLB).
The goodness of ﬁt is stable across ∆t, despite pronounced discreteness of data for very
short time intervals. The OFI variable is statistically signiﬁcant at a 95% level20 in more than
80% of samples for ∆t below one second, 100% of samples for ∆t between one second and 2
minutes, and 92% of samples for ∆t equal 5 minutes.
Notably there are many large price changes even when we consider ∆t equal to 50 millisec-
onds, but they usually correspond to high values of OFI. This is consistent with ﬁndings in
[23], where authors describe the sporadic character of order activity in modern markets. When a
subset of traders reacts to market updates in a matter of several milliseconds, this creates short
intervals of increased activity with possibly large price changes and large OFI, and many time
intervals with no activity when both variables are equal to zero. From our ﬁndings it appears
that the simple model (7) can capture both of these regimes.
When a quadratic term ˆγQ
i OFIk,i|OFIk,i| is added to the regression, the coeﬃcient ˆγQ
i
is
signiﬁcant in a handful of samples (10 out of 871) for ∆t bigger or equal to one second. For ∆t
under one second, the quadratic term is signiﬁcant in about 16% of samples, and its contribution
20using Newey-West t-statistics
31
Electronic copy available at: https://ssrn.com/abstract=1712822


<!-- PAGE 32 -->

is marginal (about 3% increase in average R2). We conclude that the relation between price
changes and OFI is linear, irrespective of a timescale.
C
Appendix: Proof of Proposition 1
Proposition 1: Assume that
1.
N(T)
T
→Λ, as T →∞, where Λ is the average arrival rate of order book events.
2. {ei}i≥1 form a covariance-stationary sequence and have a linear-process representation
ei =
∞
P
j=0
ajYi−j, where Yi is a two-sided sequence of i.i.d random variables with E[Yi] = 0
and E[Y 2
i ] = 1, and aj is a sequence of constants with
∞
P
j=0
a2
j = σ2 < ∞.
Moreover,
cov(e1, e1+n) ∼cn2(H−1) as n →∞, where 0 < H < 1 is a constant that governs the decay
of the autocorrelation function.
3. {wi}i≥1, wi = bi +si are random variables with a ﬁnite mean µπ, where π is the proportion
of order book events that correspond to trades and µ is the mean trade size. E|wi|p < ∞
for some p > 1 and P
N≥1
1
N (E| 1
N
P
i≤N
wi|q)r/q < ∞for some r, q such that 0 < r ≤q ≤∞
and r/q ≤1 −1/p.
Then
(µπ)H
σ
OFI(T)
V OLH(T)
T→∞
⇒ξ ∼N(0, 1)
where ⇒denotes convergence in distribution.
Proof: First, we note that Assumption (1) ensures N(T) →∞as T →∞. With this we can
use Assumption (3) and apply the law of large numbers for weakly dependent variables (e.g. see
Theorem 7 in [37]) to the traded volume.
V OL(T)
N(T)
=
PN(T)
i=1
wi
N(T)
→µπ, w.p.1, as T →∞,
(27)
Second, event contributions ei have a ﬁnite variance σ2 and, using Assumption (2), we
apply a central limit theorem for strongly dependent sequences (see Chapter 4.6 in [51]):
OFI(T)
σNH(T) ≡
PN(T)
i=1
ei
σNH(T) ⇒ξ, as T →∞,
(28)
where ξ ∼N(0, 1) is a standard normal random variable. Although the denominator σNH(T)
is random, it goes to inﬁnity by assumption (1) and Anscombe’s lemma ensures that we can
use such a normalization in the central limit theorem [13, Lemma 2.5.8]. Since the function
g(x) = xH, H > 0, x ≥0 is continuous, the convergence in (27) takes place almost-surely and
the limit in (27) is deterministic, we can combine (27) and (28) in the following way:
(µπ)H
σ
OFI(T)
V OLH(T) ≡
PN(T )
i=1
ei
σNH(T)
 PN(T )
i=1
wi
µπ(N(T))
H ⇒ξ, as T →∞
(29)
■
32
Electronic copy available at: https://ssrn.com/abstract=1712822
