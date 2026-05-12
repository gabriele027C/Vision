---
source_file: "lasse_heje_pedersen_et_al_efficiently_inefficient_acceptedmanuscript.pdf"
total_pages: 65
---



<!-- PAGE 1 -->

Efficiently Inefficient Markets for Assets and Asset Management
Garleanu, Nicolae; Pedersen, Lasse Heje
Document Version
Accepted author manuscript
Published in:
Journal of Finance
DOI:
10.1111/jofi.12696
Publication date:
2018
License
Unspecified
Citation for published version (APA):
Garleanu, N., & Pedersen, L. H. (2018). Efficiently Inefficient Markets for Assets and Asset Management.
Journal of Finance, 73(4), 1663-1712. https://doi.org/10.1111/jofi.12696
Link to publication in CBS Research Portal
General rights
Copyright and moral rights for the publications made accessible in the public portal are retained by the authors and/or other copyright owners
and it is a condition of accessing publications that users recognise and abide by the legal requirements associated with these rights.
Take down policy
If you believe that this document breaches copyright please contact us (research.lib@cbs.dk) providing details, and we will remove access to
the work immediately and investigate your claim.
Download date: 11. mag. 2026


<!-- PAGE 2 -->

Efficiently Inefficient Markets for Assets and Asset 
Management 
Nicolae Garleanu and Lasse Heje Pedersen 
Journal article (Accepted manuscript*) 
 
 
Please cite this article as: 
Garleanu, N., & Pedersen, L. H. (2018). Efficiently Inefficient Markets for Assets and Asset Management. 
Journal of Finance, 73(4), 1663-1712. DOI: 10.1111/jofi.12696 
This is the peer reviewed version of the article, which has been published in final form at DOI: 
https://doi.org/10.1111/jofi.12696. 
This article may be used for non-commercial purposes in accordance with Wiley Terms and Conditions for Self-
Archiving. 
 
 
 
 
 
* This version of the article has been accepted for publication and undergone full peer review but 
has not been through the copyediting, typesetting, pagination and proofreading process, which may 
lead to differences between this version and the publisher’s final version AKA Version of Record. 
 
Uploaded to CBS Research Portal: June 2019


<!-- PAGE 3 -->

Eﬃciently Ineﬃcient Markets for
Assets and Asset Management
NICOLAE GˆARLEANU and LASSE HEJE PEDERSEN∗
ABSTRACT
We consider a model where investors can invest directly or search for an asset man-
ager, information about assets is costly, and managers charge an endogenous fee. The
eﬃciency of asset prices is linked to the eﬃciency of the asset management market: if
investors can ﬁnd managers more easily, more money is allocated to active management,
fees are lower, and asset prices are more eﬃcient. Informed managers outperform after
fees, uninformed managers underperform, while the average manager’s performance de-
pends on the number of “noise allocators.” Small investors should remain uninformed,
but large and sophisticated investors beneﬁt from searching for informed active man-
agers since their search cost is low relative to capital. Hence, managers with larger and
more sophisticated investors are expected to outperform.
Keywords: asset pricing, market eﬃciency, asset management, search, information
JEL Codes: D4, D53, D83, G02, G12, G14, G23, L10
∗Gˆarleanu is at the Haas School of Business, University of California, Berkeley, CEPR, and NBER; e-
mail: garleanu@berkeley.edu. Pedersen is at AQR Capital Management, Copenhagen Business School, New
York University, and CEPR; www.lhpedersen.com. We are grateful for helpful comments from Jules van
Binsbergen, Ronen Israel, Stephen Mellas, Jim Riccobono, Tano Santos, Andrei Shleifer, Peter Norman
Sørensen, and Morten Sørensen, as well as from seminar participants at Harvard University, New York
University, Chicago Booth, UC Berkeley, AQR Capital, CEMFI, IESE, Toulouse School of Economics,
MIT Sloan, Imperial College, Cass Business School, Tinbergen Institute, Copenhagen Business School and
conference participants at NBER Asset Pricing, Queen Mary University of London, the Cowles Foundation
at Yale University, the European Financial Management Association Conference, the 7th Erasmus Liquidity
Conference, the IF2015 Annual Conference in International Finance, the FRIC’15 Conference, and the Karl
Borch Lecture. Pedersen gratefully acknowledges support from the European Research Council (ERC grant
no. 312417) and the FRIC Center for Financial Frictions (grant no. DNRF102).


<!-- PAGE 4 -->

Asset managers play a central role in making ﬁnancial markets eﬃcient, as their size allows
them to spend signiﬁcant resources on acquiring and processing information.
The asset
management market is subject to its own frictions, however, since investors must search
for informed asset managers. Indeed, institutional investors ﬂy literally around the world
to examine asset managers, assessing their investment process, trading infrastructure, risk
management, and so on. Similarly, individual investors search for asset managers, some via
local branches of ﬁnancial institutions, others via the internet or otherwise.
In this context, a number of questions arise naturally: How does the search for asset
managers aﬀect the eﬃciency of security markets? What type of manager is expected to
outperform? And which type of investors should use active investing?
We seek to address these and related questions in a model with two levels of frictions: in-
vestors’ costs of searching for informed asset managers and asset managers’ cost of collecting
information about assets. Despite this apparent complexity, the model is highly tractable
and delivers several new predictions that link the levels of ineﬃciency in the security market
and the market for asset management: (1) if investors can ﬁnd managers more easily, more
money is allocated to active management, fees are lower, and security prices are more eﬃ-
cient; (2) as search costs diminish, asset prices become eﬃcient in the limit, even if the costs
of collecting information remain large; (3) managers of assets with higher information costs
earn larger fees and are fewer, and the assets with higher information costs are less eﬃciently
priced; (4) informed managers outperform after fees while uninformed managers underper-
form after fees; (5) the net performance of the average manager depends on the number of
“noise allocators” (who allocate to randomly chosen managers) and, under certain condi-
tions, is zero or negative; (6) searching for informed active managers is attractive for large or
sophisticated investors, while small or unsophisticated investors should be uninformed; and
(7) managers with larger and more sophisticated investors are expected to outperform.
By way of background, the key benchmark is that security markets are perfectly eﬃcient
(Fama (1970)), but this leads to two paradoxes. First, no one has an incentive to collect
information in an eﬃcient market, so how does the market become eﬃcient (Grossman and
1


<!-- PAGE 5 -->

Stiglitz (1980))? Second, if asset markets are eﬃcient, then positive fees to active managers
implies ineﬃcient markets for asset management (Pedersen (2015)).
Grossman and Stiglitz (1980) show that the ﬁrst paradox can be addressed by considering
informed investing in a model with noisy supply. However, when an agent has collected
information about securities, she can invest on this information on behalf of others, so
professional asset managers arise naturally (Admati and Pﬂeiderer (1988), Ross (2005),
Garc´ıa and Vanden (2009)). We therefore introduce professional asset managers into the
Grossman-Stiglitz model.
One benchmark for the eﬃciency of asset management is provided by Berk and Green
(2004), who consider the implications of fully eﬃcient asset management markets (in the con-
text of exogenous and ineﬃcient asset prices). In contrast, we consider an imperfect market
for asset management due to search frictions, consistent with the empirical evidence of Sirri
and Tufano (1998), Jain and Wu (2000), Horta¸csu and Syverson (2004), and Choi, Laibson,
and Madrian (2010). We focus on investors’ incentive to search for informed managers and
managers’ incentives to acquire information about assets with endogenous prices, abstract-
ing from how agency problems and imperfect contracting distort asset prices (Shleifer and
Vishny (1997), Stein (2005), Cuoco and Kaniel (2011), Buﬀa, Vayanos, and Woolley (2014)).
We employ the term eﬃciently ineﬃcient to refer to the equilibrium level of ineﬃciency
given the two layers of frictions in the spirit of the Grossman-Stiglitz notion of “an equilibrium
degree of disequilibrium.” Paraphrasing Grossman-Stiglitz, prices in eﬃciently ineﬃcient
markets reﬂect information, but only partially, so that some managers have an incentive to
expend resources to obtain information, but only part of the managers, so investors have an
incentive to expend resources to ﬁnd informed managers.
Our equilibrium works as follows. Among the group of asset managers, an endogenous
number decide to acquire information about a security. Investors must decide whether to
expend search costs to ﬁnd an informed asset manager. In an interior equilibrium, investors
are indiﬀerent between searching for an informed asset manager versus uninformed investing
(and both of these options dominate the investor collecting information herself).1 When an
1Investors do not collect information on their own, since the costs of doing so are higher than the beneﬁts
2


<!-- PAGE 6 -->

investor meets an asset manager, they negotiate a fee. Asset prices are set in a competitive
noisy rational expectations market. The economy also features a group of “noise traders” (or
“liquidity traders”) who take random security positions as in Grossman-Stiglitz. Likewise,
we introduce a group of “noise allocators” who allocate capital to a random group of asset
managers, for example, because they place trust in these managers as modeled by Gennaioli,
Shleifer, and Vishny (2015).
We solve for the equilibrium number of investors who invest through managers, the
equilibrium number of informed asset managers, the equilibrium management fee, and the
equilibrium asset prices. The model features both search and information frictions, but the
solution is surprisingly simple and yields a number of clear new results.
First, we show that informed managers outperform before and after fees, while unin-
formed managers naturally underperform after fees. Investors who search for asset managers
must be compensated for their search and due diligence costs, and this compensation comes
in the form of expected outperformance after fees. Investors are indiﬀerent between active
and uninformed investing in an interior equilibrium, so larger search costs must be asso-
ciated with larger outperformance by active investors. Noise allocators invest partly with
uninformed managers and therefore may experience underperformance after fees. The asset-
weighted average manager (equivalently, their average investor) outperforms after fees if the
number of noise allocators is small and underperforms if the number of noise allocators is
large. When the average manager outperforms, searching investors would have an incentive
to “free ride” by choosing a random manager if this were free, but all manager allocations re-
quire a search cost in our baseline model. In a model extension with free search for a random
manager, the equilibrium outperformance of the average manager is zero or negative.
The model consequently helps explain a number of empirical regularities on the perfor-
mance of asset managers that are puzzling in light of the literature. Indeed, while the “old
consensus” in the literature was that the average mutual fund has no skill (Fama (1970),
to an individual due to the relatively high equilibrium eﬃciency of the asset markets. This high equilibrium
eﬃciency arises from investors’ ability to essentially “share” information collection costs by investing through
an asset manager.
3


<!-- PAGE 7 -->

Carhart (1997)), a “new consensus” has emerged that the average hides signiﬁcant cross-
sectional variation in manager skill among mutual funds, hedge funds, private equity, and
venture capital.2 For instance, Kosowski, Timmermann, Wermers, and White (2006) con-
clude that “a sizable minority of managers pick stocks well enough to more than cover their
costs.” In our model, this outperformance after fees is expected as compensation for in-
vestors’ search costs, but it is puzzling in light of the prediction of Fama (1970) that all
managers underperform after fees and the prediction of Berk and Green (2004) that all man-
agers deliver zero outperformance after fees. Furthermore, the fact that top hedge funds
and private equity managers deliver larger outperformance than top mutual funds is also
consistent with our model when investors face larger search costs in these segments.
While the data support our novel prediction that some managers outperform others,
we can test the model at a deeper level by examining whether it can also explain who
outperforms. To do so, we extend the model by considering investors and asset managers
who diﬀer in their size or sophistication. We show that large and sophisticated investors
beneﬁt from searching for an informed manager, since their search cost is low relative to
their capital. In contrast, small unsophisticated investors are better served by uninformed
investing. As a result, active investors who are small must be noise allocators, while large
active investors could be rational searching investors (or noise allocators). Hence, we predict
that large investors perform better than small investors on average, because large investors
are more likely to ﬁnd informed managers. This prediction is consistent with the ﬁndings
of Dyck and Pomorski (2016), who report that large institutional investors select managers
who outperform those of small investors.
We also predict that asset managers who have larger and more sophisticated investors
outperform those serving small unsophisticated investors. Consistent with this prediction,
managers of institutional investors outperform those of retail investors (Evans and Fahlen-
2Evidence on mutual funds is provided by Grinblatt and Titman (1989), Wermers (2000), Kacperczyk,
Sialm, and Zheng (2008), Fama and French (2010), Berk and Binsbergen (2015), and Kacperczyk, Nieuwer-
burgh, and Veldkamp (2014)), on hedge funds by Kosowski, Naik, and Teo (2007), Fung, Hsieh, Naik, and
Ramadorai (2008), Jagannathan, Malakhov, and Novikov (2010), and on private equity and venture capital
by Kaplan and Schoar (2005).
4


<!-- PAGE 8 -->

brach (2012), Dyck, Lins, and Pomorski (2013), Gerakos, Linnainmaa, and Morse (2016)).
The model also generates a number of implications of cross-sectional and time-series
variation in search costs. The important observation is that, if search costs are lower, and
therefore investors can identify informed managers more easily, then more money is allocated
to active management, fees are lower, and security markets are more eﬃcient. If investors’
search costs go to zero, then the asset market becomes eﬃcient in the limit. Indeed, as
search costs diminish, fewer and fewer asset managers with more and more asset under
management collect smaller and smaller fees, and this evolution makes asset prices more
eﬃcient even though information collection costs remain constant (and potentially large).
It may appear surprising (and counter to the result of Grossman and Stiglitz (1980)) that
markets can become close to eﬃcient despite large information collection costs, but this
result is driven by the fact that the costs are shared by investors through an increasingly
consolidated group of asset managers.
These model-implied predictions are consistent with a number of empirical ﬁndings. For
instance, if search costs have diminished over time as information technology has improved,
markets should have become more eﬃcient, consistent with the evidence of Wurgler (2000)
and Bai, Philippon, and Savov (2013), and linked to the amount of assets managed by
professional traders Rosch, Subrahmanyam, and van Dijk (2015).
In summary, we complement the literature3 by introducing a new model of asset manage-
ment and asset prices. The main innovation — search for managers — produces wide-ranging
results in a surprisingly tractable manner. Thinking through the logic of search markets
yields almost immediately some new predictions on the performance of investors and man-
agers; other predictions require deeper analysis, such as those on the magnitude of market
ineﬃciency (approximately 6%), fees, and the industrial organization of asset management.
3The related theoretical literature includes, in addition to the papers already cited, models of asset
management (Pastor and Stambaugh (2012), Vayanos and Woolley (2013), Stambaugh (2014)), noisy ra-
tional expectations models (Grossman (1976), Hellwig (1980), Diamond and Verrecchia (1981), Admati
(1985)), other models of informed trading (Glosten and Milgrom (1985), Kyle (1985)), information acqui-
sition (Van Nieuwerburgh and Veldkamp (2010), Kacperczyk, Van Nieuwerburgh, and Veldkamp (2016)),
and search models in ﬁnance (Duﬃe, Gˆarleanu, and Pedersen (2005), Lagos (2010)); we discuss the related
empirical literature in Section V.
5


<!-- PAGE 9 -->

The remainder of the paper is organized as follows. Section I lays out the basic model,
Section II provides the solution, and Section III derives the results. Section IV extends the
model to small and large investors and asset managers. Section V discusses our empirical
predictions and Section VI concludes. Appendix Appendix A contains further analysis and
proofs and Appendix B describes real-world issues related to search and due diligence of
asset managers.
I.
Model of Assets and Asset Managers
A.
Investors and Asset Managers
The economy features several types of competitive agents trading in a ﬁnancial market, as
illustrated by Figure 1. Searching investors trade directly or through asset managers, asset
managers trade on behalf of groups of investors, noise allocators make random allocations
to asset managers, and noise traders make random trades in ﬁnancial markets.
Speciﬁcally, the economy has ¯A searching investors (or “allocators”), each of whom can
(i) invest directly in asset markets after having acquired a signal s at cost k, (ii) invest
directly in asset markets without the signal, or (iii) invest through an asset manager. Due to
economies of scale, a natural equilibrium outcome is that investors do not acquire the signal,
but rather invest as uninformed or through a manager. Below (see the end of Section II.C) we
highlight weak conditions under which all realistic equilibria take this form; we therefore rule
out that investors acquire the signal. Consequently, we focus on the number A of investors
who make informed investments through a manager, inferring the number of uninformed
investors as the residual, ¯A −A.
The economy has ¯
M risk-neutral asset management ﬁrms.4 Of these asset managers,
only M elect to pay k to acquire the signal s and thereby become informed asset man-
4The total number of asset managers
¯
M can be endogenized based on an entry cost ku for being an
uninformed manager. Such endogenous entry leaves the other equilibrium conditions unaﬀected when we
interpret the information cost k as the additional cost that informed managers must incur, that is, their
total cost is ku + k. Asset management ﬁrms are risk-neutral as they face only idiosyncratic risk that can
be diversiﬁed away by their owners.
6


<!-- PAGE 10 -->

Figure 1:
Model overview.
agers. The remaining ¯
M −M managers seek to collect asset management fees and invest
without information. The number of informed asset managers is determined as part of the
equilibrium.5
To invest with an informed asset manager, investors must search for and vet managers,
which is costly. Speciﬁcally, the cost of ﬁnding an informed manager and conﬁrming that
she has the signal (i.e., performing due diligence) is given by the general continuous function
c(M, A), which depends on both the number of informed asset managers M and the number
of their investors A.6 The search cost c captures the realistic feature that most investors
spend signiﬁcant resources ﬁnding an asset manager that they trust with their money, as
described in detail in Appendix B.
We assume that all investors have constant absolute risk aversion (CARA) utility over
end-of-period consumption with risk-aversion parameter γ (following Grossman and Stiglitz
(1980)). For convenience, we express the utility as certainty-equivalent wealth — hence,
5We note that we think of the sets of managers and investors as continua (e.g., M is the mass of informed
managers), which keeps the exposition as simple as possible, but the model’s properties also obtain in a limit
of a ﬁnite-investor model.
6We require continuity of c only on [0, ∞)2 ∖{(0, 0)}, as it is natural to assume that ﬁnding an informed
manager is inﬁnitely costly if none exists, that is, c(0, A) = ∞for all A.
7


<!-- PAGE 11 -->

with end-date wealth ˜W, an investor’s utility is −1
γ log(E(e−γ ˜
W)). Each investor is endowed
with initial wealth W.
When an investor ﬁnds an asset manager and conﬁrms that the manager has the technol-
ogy to obtain the signal, they negotiate the asset management fee f. The fee is set through
Nash bargaining and, at this bargaining stage, both the manager’s information acquisition
cost and the investor’s search cost are sunk.7
We note that while the fee f is a total payment, which is the relevant quantity for
the agents’ utilities, it can be achieved through an unlimited number of combinations of
funds invested and percentage fees (as is typical in the literature). For instance, economic
outcomes are unchanged if investors double their dollar investment in the fund and pay half
the percentage fee, while the manager puts half of the portfolio in cash (or an index).
Lastly, the economy features a group of “noise traders” and a group of “noise allocators.”
As in Grossman and Stiglitz (1980), noise traders buy an exogenous number of shares of the
security, ¯q−q, as described below. Noise traders create uncertainty about the supply of shares
and are used in the literature to capture the fact that it can be diﬃcult to infer fundamentals
from prices.
Noise traders are also called “liquidity traders” in some papers, and their
demand can be justiﬁed by a liquidity need, hedging demand, or behavioral explanations.
Following the tradition of noise traders, we introduce the concept of “noise allocators,”
of total mass N ≥0, who allocate their funds across randomly chosen asset managers. Noise
allocators play a similar role in the market for asset management to the one that noise traders
play in the market for assets — speciﬁcally, noise allocators can make it diﬃcult for searching
investors to determine whether a manager is informed by looking at whether she has other
investors. Further, the existence of noise allocators changes the performance characteristics
across managers and investors, giving rise to novel model predictions, particularly when we
introduce agent heterogeneity in Section IV. Noise allocators pay the general fee f, which
we can view as an assumption for simplicity. However, we endogenize the fee and behavior
7Negotiation over terms is a common feature of the interaction between institutional investors and asset
managers, but is much less common for individual investors. For individual investors, our assumption can
be interpreted as the result of other forms of (imperfect) competition among managers, for instance, as in
Garc´ıa and Vanden (2009). The main feature needed is that the fee provides incentives to search.
8


<!-- PAGE 12 -->

of noise allocators in Appendix A.4.
B.
Assets and Information
We adopt the asset-market structure of Grossman and Stiglitz (1980) and focus on the
consequences of introducing asset managers into this framework. Speciﬁcally, there exists
a risk-free asset normalized to deliver a zero net return, and a risky asset with payoﬀv
distributed normally with mean ¯v and standard deviation σv. Agents can obtain a signal s
of the payoﬀ, where
s = v + ε.
(1)
The noise ε has mean zero and standard deviation σε, is independent of v, and is normally
distributed.
The risky asset is available in stochastic supply given by q, which is jointly normally
distributed with, and independent of, the other exogenous random variables. The mean
supply is ¯q and the standard deviation of the supply is σq. We think of the noisy supply as
the number of shares outstanding ¯q plus the supply q −¯q from the noise traders.
Given this asset market, uninformed investors buy a number of shares xu as a function of
the observed price p, to maximize their utility uu (certainty-equivalent wealth), taking into
account the fact that the price p may reﬂect information about the value:
uu(W) = −1
γ log

E

max
xu E
 e−γ(W+xu(v−p))|p

= W + uu(0) ≡W + uu.
(2)
Because of the CARA utility function, an investor’s wealth level simply shifts his utility
function without aﬀecting his optimal behavior. We therefore deﬁne the scalar uu as the
wealth-independent part of the utility function (a scalar that naturally depends on the
asset-market equilibrium, in particular, on price eﬃciency).
Asset managers observe the signal and invest in the best interest of their investors. This
informed investing gives rise to the gross utility ui of an active investor (i.e., not taking into
9


<!-- PAGE 13 -->

account his search cost and the asset management fee — we study those, and specify their
impact on the ex-ante utility, later):
ui(W) = −1
γ log

E

max
xi E
 e−γ(W+xi(v−p))|p, s

= W + ui(0) ≡W + ui.
(3)
As above, we deﬁne the scalar ui as the wealth-independent part of the utility function. The
gross utility of an active investor diﬀers from that of an uninformed investor via conditioning
on the signal s.
We note that all investors with an informed manager want the same portfolio xi since
investors are homogeneous. Hence, we simply assume that the manager oﬀers the portfolio
xi for anyone investing W. When we introduce small and large investors in Section IV,
investors with smaller absolute risk aversions prefer larger multiples of the same xi, which
can naturally be achieved through a larger investment in the same fund.
C.
Equilibrium Concept
We ﬁrst consider the (partial) equilibrium in the asset market given the numbers of
informed and uninformed investors. We denote the mass of informed investors by I and note
that it is the sum of the number A of rational investors who decide to search for a manager
and the number of noise allocators who happen to ﬁnd an informed manager, where the latter
is the total number N of noise allocators times the fraction M/ ¯
M of informed managers:
I = A + N M
¯
M .
(4)
Clearly, the remaining investors, ¯A + N −I, invest as uninformed, either directly or via an
uninformed manager. An asset-market equilibrium is an asset price p such that the asset
market clears:
q = Ixi + ( ¯A + N −I)xu,
(5)
10


<!-- PAGE 14 -->

where xi is the demand that maximizes the utility of informed investors (3) given p and the
signal s, and xu is the demand of uninformed investors (2). The market-clearing condition
equates the noisy supply q with the total demand from all informed and uninformed investors.
Next, we deﬁne a general equilibrium for assets and asset management as a number of
informed asset managers M, a number of active investors A, an asset price p, and asset
management fees f such that (i) no manager would like to change her decision of whether
to acquire information, (ii) no investor would like to switch status from active (with an
associated utility of W +ui −c−f) to uninformed (conferring utility W +uu) or vice-versa,
(iii) the price is an asset-market equilibrium, and (iv) the asset management fees are the
outcome of Nash bargaining.
II.
Solving the Model
A.
Asset-Market Equilibrium
We ﬁrst derive the asset-market equilibrium taking as given the number of informed
investors I. Later we solve for the equilibrium number of searching investors and managers,
which yields I by (4). For a given I, the unique linear asset-market equilibrium is as in
Grossman and Stiglitz (1980), but for completeness we record the main results here.8
In the linear equilibrium, an informed agent’s demand for the asset is a linear function
of prices and signals, and the price is a linear function of the signal and the noisy supply,
p = θ0 + θs ((s −¯v) −θq(q −¯q)) ,
(6)
where the coeﬃcients θ are given in Appendix A.5. The key property of the price is its
eﬃciency (or informativeness), which Grossman and Stiglitz (1980) deﬁne as var(v|s)
var(v|p). For
8Our setup diﬀers from that of Grossman and Stiglitz (1980) by a change of variables, which leads to
some superﬁcial diﬀerences in the results. Palvolgyi and Venter (2014) derive interesting nonlinear equilibria
in the Grossman and Stiglitz (1980) model.
11


<!-- PAGE 15 -->

convenience, we concentrate on the quantity
η ≡log
σv|p
σv|s

= 1
2 log
var(v|p)
var(v|s)

,
(7)
which represents the price ineﬃciency. This quantity records the amount of uncertainty
about the asset value for someone who only knows the price p, relative to the uncertainty
remaining when one knows the signal s. The price ineﬃciency is a positive number, η ≥0,
since the price is a noisy version of the signal, var(v|p) ≥var(v|p, s) = var(v|s). Naturally,
a higher η corresponds to a more ineﬃcient asset market while zero ineﬃciency corresponds
to a price that fully reveals the signal.
The price ineﬃciency η is linked to investors’ value of information.
Indeed, η gives
the relative utility of investing based on the manager’s information (ui) versus investing as
uninformed (uu):
γ(ui −uu) = η.
(8)
This is an important result, as the relative utility ui−uu plays a central role in the remainder
of the paper, aﬀecting investors’ incentive to search, asset management fees, and managers’
incentive to acquire information.
The ineﬃciency η can be written as an explicit function of the number of informed
investors I:
η = −1
2 log

1 −
σ2
qσ2
ε
I2/γ2 + σ2
qσ2
ε
σ2
v
σ2
ε + σ2
v

∈(0, ∞).
(9)
We see that η is decreasing in I, which is natural since, when there are more informed in-
vestors, asset prices become less ineﬃcient (lower η), implying that informed and uninformed
investors receive more similar utilities (lower ui −uu).
We note that the price ineﬃciency does not depend directly on the number of asset
managers M.
What determines the asset price eﬃciency is the risk-bearing capacity of
agents investing based on the signal, and this risk-bearing capacity is ultimately determined
12


<!-- PAGE 16 -->

by the number of informed investors (not the number of managers they invest through).
The number of asset managers does aﬀect asset price eﬃciency indirectly, however, since M
aﬀects I as seen in (4), and, importantly, since the number of searching investors A and the
number of asset manages are determined jointly in equilibrium, as we shall see below.
B.
Asset Management Fee
The asset management fee is set through Nash bargaining between an investor and a
manager. The bargaining outcome depends on each agent’s utility in the events of agreement
and no agreement (the latter is called the “outside option”). The investor’s utility when
agreeing on a fee f is W −c −f + ui. If no agreement is reached, the investor’s outside
option is to invest as uninformed with his remaining wealth, yielding a utility of W −c + uu
as the cost c is already sunk.9 Hence, the investor’s gain from agreement is ui −uu −f.
Similarly, the asset manager’s gain from agreement is the fee f. This is true because the
manager’s information cost k is sunk and there is no marginal cost to taking on the investor.
The bargaining outcome maximizes the product of the utility gains from agreement:
max
f
(ui −uu −f) f.
(10)
The solution is the equilibrium asset management fee f given by
f = η
2γ ,
[equilibrium asset management fee]
(11)
using ui −uu = η/γ from equation (8). This equilibrium fee is simple and intuitive: The fee
would naturally have to be zero if asset markets were perfectly eﬃcient, so that no beneﬁt
of information existed (η = 0), and increases in the size of the market ineﬃciency. Indeed,
active asset management fees can be viewed as evidence that investors believe that security
9The investor’s outside option is equal to the utility of searching for another manager in an interior
equilibrium. Hence, we can think of the investor’s bargaining threat as walking away to invest on his own or
to ﬁnd another manager. Note also that we specify the bargaining objective in terms of certainty-equivalent
wealth, which is natural and tractable.
13


<!-- PAGE 17 -->

markets are less than fully eﬃcient.
We next derive investors’ and managers’ decisions in an equally straightforward manner.
Indeed, an attractive feature of this model is that it is very simple to solve, yet provides
powerful results.
C.
Investors’ Decision to Search for Asset Managers
An investor optimally decides to look for an informed manager as long as
ui −c −f ≥uu.
(12)
Recalling the equality η = γ(ui −uu), the investor’s optimality condition can be written as
η ≥γ(c + f). This relation must hold with equality in an “interior” equilibrium (i.e., an
equilibrium in which strictly positive amounts of investors decide to invest as uninformed and
through asset managers — as opposed to all investors making the same decision). Inserting
the equilibrium asset management fee (11), we have already derived the investor’s indiﬀerence
condition: c =
η
2γ.
Using similar straightforward arguments, we see that an investor would prefer using
an asset manager to acquiring the signal singlehandedly provided that k ≥c + f. Using
the equilibrium asset management fee derived in equation (11), the condition that asset
management is preferred to buying the signal can be written as k ≥2c. In other words,
ﬁnding an asset manager should cost at most half as much as actually being one, which
seems to be a condition that is clearly satisﬁed in the real world. We can also make use of
(13) to express this condition equivalently as A ≥2M, that is, there must be at least two
searching investors for every manager, which is also a realistic implication.
Finally, we note that we have assumed that searching investors allocate to an active
manager only when they have paid a search cost to ensure that the manager is informed. We
could also allow investors to pick a random manager without paying a search cost, perhaps
even using information on managers’ assets under management (AUM). We consider such
14


<!-- PAGE 18 -->

extensions in Section III.A.1 and Appendix A.2.
D.
Entry of Informed Asset Managers
A prospective informed asset manager must pay the cost k to acquire information. On
the other hand, by becoming informed, the manager can expect to have more investors.
Speciﬁcally, each manager receives a noisy number of investors, but, since managers are risk
neutral, they optimize the expected fee revenue net of information costs.
An uninformed manager expects N/ ¯
M investors, that is, the number of noise allocators
divided by the total number of managers.
An informed manager expects A/M + N/ ¯
M
investors since she expects a fraction of the searching investors in addition to the noise
allocators. Therefore, she chooses to become informed provided that the expected extra fee
revenue covers the cost of information:
f A
M ≥k.
(13)
This manager condition must hold with equality for an interior equilibrium, and we can
easily insert the equilibrium fee (11) to get M = ηA
2γk.
E.
General Equilibrium for Assets and Asset Management
We focus on interior equilibria, but we provide a complete equilibrium characterization
in Appendix A.1. We have arrived at the following two indiﬀerence conditions:
η(I)
2γ
= c (M, A)
[investors’ indiﬀerence condition]
(14)
η(I)
2γ
= M
A k,
[asset managers’ indiﬀerence condition]
(15)
where η is a function of I = A + N M
¯
M given explicitly by (9). Hence, solving the general
equilibrium comes down to solving these two explicit equations in two unknowns (A, M).
Recall that a general equilibrium for assets and asset management is a four-tuple (p, f, A, M),
15


<!-- PAGE 19 -->

but we have eliminated p by deriving the market eﬃciency η in a partial asset market
equilibrium and we have eliminated f by expressing it in terms of η. We can solve equations
(14) and (15) explicitly when the search-cost function c is speciﬁed appropriately as we
show in the following example, but the remainder of the paper provides results for general
search-cost functions.
Example: Closed-Form Solution. A cost speciﬁcation motivated by the search literature is
c (M, A) = ¯c
 A
M
α
for M > 0
and
c(M, A) = ∞for M = 0,
(16)
where the constants α > 0 and ¯c > 0 control the nature and magnitude of search frictions.
The idea is that informed asset managers are easier to ﬁnd if a larger fraction of all asset
managers are informed, while performing due diligence (which requires the asset manager’s
time and cooperation) is more diﬃcult in a tighter market with a larger number of searching
investors. With this search cost function, equations (14) and (15) can be combined to yield
η = 2γ (¯ckα)
1
1+α ,
(17)
which shows how search costs and information costs determine market ineﬃciency η. We
then derive the equilibrium number of informed investors I from (9):
I = γσqσε
s
σ2
v
σ2
ε + σ2
v
1
1 −e−2η −1 = γσqσε
s
σ2
v
σ2
ε + σ2
v
1
1 −e−4γ(¯ckα)
1
1+α −1 .
(18)
The number of informed managers can be linearly related to the number of searching investors
based on (15) and (17),
M =
η
2γkA =
 ¯c
k

1
1+α A,
(19)
so the number of managers per investor M/A depends on the magnitude of the search cost
16


<!-- PAGE 20 -->

¯c relative to the information cost k. Combining (19) with the identity I = A + M N
¯
M yields
the solution for A,
A = I

1 + N
¯
M
 ¯c
k

1
1+α−1
,
(20)
concentrating on parameters for which A < ¯A.
When η is small (a reasonable value is η = 6%, as we show in Section III.C), we can
approximate the number of informed investors more simply by
I ∼=
γ
(2η)1/2
σqσεσv
(σ2
ε + σ2
v)1/2 =
γ1/2
2(¯ckα)
1
2(1+α)
σqσεσv
(σ2
ε + σ2
v)1/2,
(21)
which illustrates more directly how search costs ¯c and information costs k lower the number
of informed investors, while risk aversion γ and noise trading σq raise I.
Figure 2 provides a graphical illustration of the determination of equilibrium as the
intersection of the managers’ and investors’ indiﬀerence curves. The ﬁgure is plotted based
on the parametric example above,10 but it also illustrates the derivation of equilibrium for a
general search function c(M, A).
Speciﬁcally, Figure 2 shows various possible combinations of the numbers of active in-
vestors, A, and informed asset managers, M. The solid blue line depicts investors’ indiﬀer-
ence condition (14). When (A, M) is above and to the left of the solid blue line, investors
prefer to search for asset managers because managers are easy to ﬁnd and attractive to ﬁnd
due to the limited eﬃciency of the asset market. In contrast, when (A, M) is below and to
the right of the blue line, investors prefer to be uninformed as the costs of ﬁnding a manager
are not outweighed by the beneﬁts. The indiﬀerence condition is naturally increasing as
10We use the following parameters. Starting with investors, the total number of optimizing investors is
¯A = 108, the number of noise allocators is N = 108, and absolute risk aversion is γ = 3 × 10−5, which
corresponds to a relative risk aversion γR = 3 and an average invested wealth of W = 105. The total number
of managers is ¯
M = 4, 000. Turning to asset markets, the number of shares outstanding is normalized to
¯q = 1, the expected ﬁnal value of the asset equals total wealth ¯v = ( ¯A + N)W = 2 × 1013, asset volatility is
20% (i.e., σv = 0.2¯v), the signal about the asset has 30% noise (σε = 0.3¯v), and the noise in the supply is
20% of shares outstanding (σq = 0.2). Lastly, the frictions are given by the cost of being an informed asset
manager k = 2 × 107 and the search cost parameters α = 0.8 and ¯c = 0.3.
17


<!-- PAGE 21 -->

investors are more willing to be active when there are more asset managers.
Similarly, the dashed red line shows managers’ indiﬀerence condition (15). When (A, M)
is above the red line, managers prefer not to incur the information cost k since too many
managers are seeking to service investors. Below the red line, managers want to become
informed. Interestingly, the manager indiﬀerence condition is hump-shaped. The reason
is that, when the number of active investors increases from zero, the number of informed
managers also increases from zero, since managers are encouraged to earn the fees paid by
searching investors. However, the total fee revenue is the product of the number of active
investors A and the fee f.
The equilibrium fee f decreases with the number of active
investors because active investment increases asset market eﬃciency, thus reducing the value
of asset management services.
Hence, when so many investors have become active that
this fee reduction dominates, additional active investment decreases the number of informed
managers.
The economy in Figure 2 has two equilibria. In one equilibrium (A, M) = (0, 0), which
means that no investor searches for asset managers as there is no one to be found, and no
asset manager sets up operation because there are no investors. We naturally focus on the
more interesting equilibrium with A > 0 and M > 0.
Figure 2 also helps illustrate the set of equilibria more generally. First, if the search
and information frictions c and k are strong enough, then the blue line is initially steeper
than the red line and the two lines cross only at (A, M) = (0, 0), which means that this
equilibrium is unique due to the severe frictions. Second, if the frictions c and k are mild
enough, then the blue line ends up below the red line at the right-hand side of the graph
with A = ¯A. In this case, all investors being active is an equilibrium. Lastly, when frictions
are intermediate, as in Figure 2, the largest equilibrium is an interior equilibrium, that is,
A < ¯A and M < ¯
M. We focus on such interior equilibria since they are the most realistic
and interesting ones. We note that while Figure 2 has only a single interior equilibrium,
more interior equilibria may exist for other speciﬁcations of the search cost function (e.g.,
because the investor indiﬀerence condition starts above the origin, or because it can “wiggle”
18


<!-- PAGE 22 -->

0
0.5
1
1.5
2
2.5
3
3.5
x 10
7
0
200
400
600
800
1000
1200
1400
1600
Number of searching investors, A
Number of informed asset managers, M
 
 
investors
search
investors
passive
managers
exit
managers
enter
Investor indifference condition
Manager indifference condition
Figure 2:
Equilibrium for assets and asset management. This ﬁgure illustrates
the equilibrium determination of the number of searching investors A and the number of
informed asset managers M. Each investor decides whether to search for an asset manager
or invest uninformed depending on the actions (A, M) of everyone else; similarly, managers
decide whether to acquire information. The right-most crossing of the indiﬀerence conditions
is an interior equilibrium.
enough to create additional crossings of the two lines).
III.
Equilibrium Properties
A.
Performance of Asset Managers and Investors
We start by considering some basic properties of performance in eﬃciently ineﬃcient
markets. We use the term outperformance to mean that an informed investor’s performance
yields a higher expected utility than that of an uninformed investor, and vice versa for
underperformance.
We note that an investor’s expected utility is directly linked to his
(squared) Sharpe ratio, the expectation of which is proportional to the expected return.11
11See Section III.C and the proof of Proposition 7 for these basic results of a mean-variance framework.
19


<!-- PAGE 23 -->

Proposition 1 (Performance): In a general equilibrium for assets and asset management:
(i) Informed asset managers outperform uninformed investing before and after fees, ui −
f > uu. Uninformed asset managers underperform after fees.
(ii) Searching investors’ outperformance net of fees just compensates their search costs in
an interior equilibrium, ui −f −c = uu. Larger equilibrium search frictions imply
higher net outperformance for informed managers.
(iii) The asset-weighted average manager (or, equivalently, the asset-weighted average in-
vestor) outperforms after fees if and only if the number N of noise allocators is small
relative to the number A of searching investors, A ≥N
 1 −2M
¯
M

.
The above results follow from the fact that investors must have an incentive to incur
search costs to ﬁnd an asset manager and pay the asset management fees. Investors who
have incurred a search cost can eﬀectively predict manager performance. Interestingly, this
performance predictability is larger in an asset management market with larger search costs.
To the extent that search costs are larger for hedge funds than mutual funds, larger for
international equity than domestic equity funds, larger for insurance products than mutual
funds, and larger for private equity than public equity funds, these resulte can explain why
the former asset management funds may deliver larger outperformance and why the markets
they invest in are less eﬃcient.
A.1.
Searching for a Manager Based on Assets Under Management
So far we have assumed that investors can either invest as uninformed or pay a search
cost to ﬁnd an informed manager. Here we illustrate the implications of allowing investors,
at a lower cost, to also draw a random manager according to some mechanism. This form of
uninformed investment in the market for asset management parallels the uninformed invest-
ment in the security market in Grossman and Stiglitz (1980), that is, investment based on
freely available information. To make this alternative as attractive as possible, we take this
20


<!-- PAGE 24 -->

search cost to be zero. Furthermore, we assume that it is more likely to draw a larger man-
ager; more precisely, the speciﬁc mechanism we consider implies that the investor essentially
obtains the industry-wide after-fee return. We analyze this extended model in Appendix A.2.
As a more information-heavy alternative, below we consider an example in which investors
are allowed to make full use of the entire AUM distribution.
For some parameters, the equilibrium in the baseline model is the same as the equilibrium
in the extended model. Indeed, if the asset-weighted net return is worse than that from
uninformed investing, which can be determined based on the condition in Proposition 1(iii),
then the equilibrium does not change as this search for a random manager is not attractive.
If not, then the equilibrium in the extended model changes: some investors will switch
from being uninformed or active to searching for a random manager, until the point at which
the asset-weighted manager’s net performance matches that of uninformed investing.
Proposition 1′: In an interior equilibrium of the extended model, the asset-weighted aver-
age manager’s outperformance after fees is zero, pIui + (1 −pI)uu −f = uu, where pI is the
fraction of assets managed by informed managers.
Hence, it may be no coincidence that the average manager in the data delivers similar
performance to index funds. Put diﬀerently, in an interior equilibrium of our extended model,
the assumption of Berk and Green (2004) that asset managers deliver zero outperformance
after fees holds at the level of the overall asset management industry, but not at the level of
each individual manager.
To understand the intuition for this result, recall that an asset manager’s AUM is noisy.
Hence, while informed managers have higher AUM on average, any one informed manager
could have lower AUM than any one uninformed manager by chance. Therefore, picking
managers based on their AUM results in a mixture of informed and uninformed managers.
Further, while informed managers are expected to outperform net of fees, uninformed man-
agers underperform after fees (because they charge a fee even though they don’t add value).
21


<!-- PAGE 25 -->

Therefore, a mixture of these managers can be (and indeed will be, in an interior equilib-
rium) just as good as direct uninformed investing and just as good as paying a search cost
to ﬁnd a manager who is surely informed.
Example: distribution of manager size and performance. The underperformance of unin-
formed managers (−f) is as large in magnitude as the outperformance of informed managers
(ui −f −uu = f). Therefore, picking a random manager is a good investment if the chance
of getting an informed manager is at least 50%. In the numerical example of Section II.E,
there are more uninformed than informed managers in equilibrium, so picking a random man-
ager would not be a good investment even if it were free. However, the informed managers
have more investors on average, so investing with the “market portfolio” of managers would
be better. Nevertheless, such an AUM-weighted manager investment is also dominated by
investing directly as uninformed in the example.
We can further reﬁne the example to explicitly consider the size distribution across asset
managers. For instance, suppose that each manager receives a number of noise allocators
that is exponentially distributed with mean N/ ¯
M (i.e., exponential parameter ¯
M/N). This
distribution can arise if noise allocators invest based on news stories, and news stories about
each manager arrive at Poisson jumps such that each manager receives media attention for an
exponentially-distributed time period. Each informed manager also receives A/M searching
investors for sure (i.e., without randomness, for simplicity).
In this case, managers with fewer than A/M investors must be uninformed.
Among
managers with any number of investors greater than A/M, a constant proportion (47%,
given the parameters of our numerical example) are informed, and the remainder (53%) are
uninformed.12 Hence, if we further extended the model to allow investors to pick a manager
of any speciﬁc size (at some cost), then investors would not want to do so given that only
47% of managers are informed. Instead, investors would still prefer to either pay a search
cost to ensure ﬁnding an informed manager or invest as uninformed.
12Speciﬁcally, this proportion equals Me
¯
M
N
A
M /(Me
¯
M
N
A
M + ¯
M −M).
22


<!-- PAGE 26 -->

A.2.
On the Impossibility of Eﬃcient Asset Management: A Paradox
The Grossman-Stiglitz paradox shows that security markets cannot be fully eﬃcient since,
if they were, no one would have an incentive to collect information. A similar paradox exists
for asset management markets: public signals about asset managers such as their AUM
cannot fully reveal which managers are informed since, if they did, no investor would have
an incentive to search and do due diligence. This insight can be seen rigorously in the version
of our model in which investors can invest based on AUM for free. If the number of noise
allocators goes to zero, then AUM becomes very informative, leading fewer investors to pay
for search, and, eventually, the only equilibrium is one in which no investor searches and
no manager is informed. This equilibrium is fragile, however, as the market is so ineﬃcient
that investors have strong incentives to ﬁnd an informed manager (should any exist), but,
as soon as someone succeeds in ﬁnding an informed manager, other investors can free ride.
Thus, noise allocators are needed to resolve this paradox just as noise traders are needed for
the Grossman-Stiglitz paradox.
A.3.
Meaning of Eﬃciently Ineﬃcient
We say that the asset price is fully eﬃcient if η = 0, meaning that the price fully reﬂects
the signal. In equilibrium, asset prices always involve some degree of ineﬃciency (η > 0),
but eﬃciency can arise as a limit, as we shall see in the next section.
There can be several measures of the ineﬃciency of asset management markets. One mea-
sure of this ineﬃciency is the aggregate cost of locating asset managers plus their aggregate
information cost, cA + kM. As we shall see next, this aggregate asset management ineﬃ-
ciency can be reduced towards zero if the search cost is reduced. Another measure of asset
management eﬃciency could be the extent to which AUM reﬂects a manager’s information
as discussed in the paradox above.
We employ the term eﬃciently ineﬃcient to refer to the equilibrium level of ineﬃciency
given the frictions (as discussed in the introduction). This deﬁnition applies both to markets
for securities and asset managers.
23


<!-- PAGE 27 -->

B.
Comparative Statics
We next consider how the economic outcomes depend on the exogenous parameters. To
analyze such comparative statics in a model that could have multiple equilibria, we focus on
the equilibrium with the largest value of I simply because we need to pick a given equilibrium.
We start with the implications of changing the search cost.
Proposition 2 (Search for asset management):
(i) Consider two search cost functions, c1 and c2, with c1 > c2 and the corresponding
largest-I equilibria. In the equilibrium with the lower search costs c2, the number of
active investors A and the number of informed investors I are larger, the number
of managers M may be higher or lower, the asset price is more eﬃcient, the asset
management fee f is lower, and the total fee revenue f(A + N) may be either higher
or lower.
(ii) If {cj}j=1,2,3,... is a decreasing series of cost functions that converges to zero at every
point, then A = ¯A when the cost is suﬃciently low, that is, all rational agents search
for managers. If the number of investors { ¯Aj} increases towards inﬁnity as j goes to
inﬁnity, then η goes to zero (full price eﬃciency in the limit), the asset management fee
f goes to zero, the number of asset managers M goes to zero, the number of investors
per manager goes to inﬁnity, and the total fee revenue of all asset managers f(A + N)
goes to zero.
The above proposition provides several intuitive results, which we illustrate in Figure 3.
As can be seen in the ﬁgure, lower search costs mean that the investor indiﬀerence curve
moves down, leading to a larger number of active investors in equilibrium. This result is
natural, since investors have stronger incentives to enter when their cost of doing so is lower.
The number of asset managers can increase or decrease (as in the ﬁgure), depending on
the location of the hump in the manager indiﬀerence curve. This ambiguous change in M
is due to two countervailing eﬀects. On the one hand, a larger number of active investors
increases the total management revenue that can be earned given the fee. On the other hand,
24


<!-- PAGE 28 -->

0
0.5
1
1.5
2
2.5
3
3.5
x 10
7
0
200
400
600
800
1000
1200
1400
1600
Number of searching investors, A
Number of informed asset managers, M
 
 
Investor indifference condition
Investor condition, lower search cost
Manager indifference condition
Figure 3:
Equilibrium eﬀect of lower investor search costs. This ﬁgure illustrates
that lower costs of ﬁnding asset managers implies more active investors in equilibrium and
hence increased asset market eﬃciency.
more active investors means more eﬃcient asset markets, leading to lower asset management
fees. When the search cost is low enough, the latter eﬀect dominates and the number of
managers starts to fall as seen in part (ii) of Proposition 2.
As search costs continue to fall, the asset management industry becomes increasingly
concentrated, with progressively fewer asset managers managing the money of more investors.
This leads to an increasingly eﬃcient asset market and market for asset management.
Perhaps surprisingly, the security market can become almost eﬃcient despite a high
Grossman-Stiglitz cost k. This ﬁnding is driven by the fact that, as search costs decline,
investors essentially share the information cost more eﬃciently. Indeed, the aggregate infor-
mation cost incurred is kM, which decreases towards zero as the asset management industry
consolidates.
We next consider the eﬀect of changing the cost of acquiring information, which depends
on some realistic properties of the search function.13
13Proposition 3 relies on a regularity condition on the search cost function c. On the one hand, ﬁnding an
25


<!-- PAGE 29 -->

0
0.5
1
1.5
2
2.5
3
3.5
x 10
7
0
200
400
600
800
1000
1200
1400
1600
Number of searching investors, A
Number of informed asset managers, M
 
 
Investor indifference condition
Manager indifference condition
Manager condition, lower information cost
Figure 4:
Equilibrium eﬀect of lower information acquisition costs. This ﬁgure
illustrates that lower costs of acquiring information about assets implies more active investors
and more asset managers in equilibrium and hence increased asset market eﬃciency.
Proposition 3 (Information cost): Suppose that c satisﬁes
∂c
∂M ≤0 and
∂c
∂A ≥0. As the
cost of information k decreases, the largest equilibrium changes as follows.
The number
of informed investors I increases, the number of asset managers M increases, asset-price
eﬃciency increases, and the asset management fee f goes down.
The number of active
investors A may increase or decrease.
The results of this proposition are illustrated in Figure 4. As can be seen in the ﬁgure,
a lower information cost for asset managers moves their indiﬀerence curve out. This leads
to a larger number of asset managers and informed investors in equilibrium, which increases
asset-price eﬃciency. Finally, we consider the eﬀect of risk.
informed manager is easier if a larger fraction of all managers are informed:
∂c
∂M ≤0. On the other, hand
it is more challenging if more investors are competing for the asset manager’s time and attention:
∂c
∂A ≥0.
This may help explain, for instance, why many managers have a minimum investment size. That said, there
are potential channels, such as word-of-mouth communication, through which a larger number of searching
investors may alleviate search costs. Our condition is satisﬁed for the search cost function considered in our
example in equation (16).
26


<!-- PAGE 30 -->

Proposition 4 (Risk): Suppose that
∂c
∂M ≤0 and
∂c
∂A ≥0. An increase in the fundamental
volatility σv or in the noise-trading volatility σq leads to a larger number of active investors
A, informed investors I, and informed asset managers M. The eﬀect on the eﬃciency of
asset prices and the asset management fee f, as well as on total fee revenues f(A + N), is
ambiguous. The same results obtain with a proportional increase in (σv, σε) or in all risks
(σv, σε, σq).
C.
Economic Magnitude of Market Ineﬃciency
While the debate in ﬁnancial economics is often centered around whether the market is
ineﬃcient, the Grossman-Stiglitz insight implies that what we should really be asking is how
ineﬃcient. Our model can help provide an answer. As we show below, the answer is neither
“yes” nor “no,” but rather “6%.”
To illustrate the economic magnitudes of some of the interesting properties of the model
in a simple way, it is helpful to write our predictions is relative terms. Speciﬁcally, as seen
in Section IV, investors’ preferences can be written in terms of the relative risk aversion γR
and wealth W such that γ = γR/W. Further, the asset management fee can be viewed as
a ﬁxed proportion of the investment size, and we deﬁne the proportional fee as f % = f/W.
We make the precise assumptions that all investors have relative risk aversion of γR = 3 and
that the equilibrium percentage asset management fee is f % = 1%.
The market ineﬃciency η can then be expressed in terms of the proportional asset man-
agement fee and relative risk aversion as
η = 2fγ = 2f %γR = 2 · 1% · 3 = 6%.
(22)
In other words, the standard deviation of the true asset value from the perspective of a
trader who knows the signal is 6% smaller than that of a trader who only observes the price.
Further, we see that the ineﬃciency is greater in markets with higher percentage fees (e.g.,
private equity versus public) and during times of high risk aversion (e.g., crisis periods).
27


<!-- PAGE 31 -->

We can also characterize the ineﬃciency by the diﬀerence in squared gross Sharpe ratios
attainable by informed (SRi) versus uninformed (SRu) investors using a log-linear approxi-
mation:14
E(SR2
i ) −E(SR2
u) ∼= 2η = 4f %γR = 4 · 1% · 3 = 0.12.
(23)
Hence, if uninformed investing yields an expected squared Sharpe ratio of 0.42 (similar to
that of the market portfolio), informed investing must yield an expected squared Sharpe
ratio around 0.532 (i.e., 0.532 −0.42 = 0.12). We see that, at this realistic fee level, the
implied diﬀerence in Sharpe ratios between informed and uninformed managers is relatively
small and hard to detect empirically. Of course, while the model-predicted magnitude of
ineﬃciency appears reasonable, our model is quite stylized and needs to be supplemented
with empirical analysis.
IV.
Small versus Large Investors and Asset Managers
So far we have considered an economy in which all investors and managers are identical ex
ante. In the real world, however, investors diﬀer in their wealth and ﬁnancial sophistication
and managers diﬀer in their education and investment approach. Should large asset owners
such as high-net-worth families, pension funds, or insurance companies invest diﬀerently
than small retail investors, and what type of asset managers are more likely to be informed?
To address these questions, we extend the model to capture diﬀerent types of investors
and managers.
Each investor a ∈[0, ¯A] has an investor-speciﬁc search cost ca, where a
smaller search cost corresponds to greater sophistication. Further, investors have diﬀerent
levels of absolute risk aversion, γa. We can interpret these as arising from diﬀerent levels
14Since each type of investor n = i, u chooses a position of x =
En(v)−p
γVarn(v), the investor’s conditional
Sharpe ratio is SRn = |En(v)−p|
√
Varn(v), where En and Varn are the mean and variance conditional on n’s infor-
mation. We have η = log

E
h
e−1
2 (v−p) E[v−p|p]
var(v|p)
i
−log

E
h
e−1
2 (v−p) E[v−p|s,p]
var(v|s)
i
, which is approximated by
1
2

E
h
(v −p) E[v−p|s,p]
var(v|s)
i
−E
h
(v −p) E[v−p|p]
var(v|p)
i
, yielding (23) because the conditional variances are constant.
28


<!-- PAGE 32 -->

of wealth Wa or relative risk aversion γR
a , which corresponds to a constant absolute risk
aversion of γa = γR
a /Wa.15 The characteristics ca, γR
a , and Wa are drawn randomly and are
independent both of each other and across agents. Also, noise allocators n ∈[0, N] have
(cn, γR
n , Wn) drawn independently from the same distribution.16
To capture diﬀerent types of asset managers, we assume that each manager m ∈[0, ¯
M]
has a manager-speciﬁc cost km of becoming informed — one can think of this feature as skill
or education — and that they are ordered according to this cost. Hence, managers with a
lower m have lower costs, that is, the function k : [0, ¯
M] →R is increasing.
We solve the model similarly to before, but we leave the details to Appendix A.3.
A.
Who Should be Active?
We ﬁrst study which types of investors should search for an active manager.
Proposition 5 (Which investors should be active?): Investor a should invest with an active
manager if he has large wealth Wa, low relative risk aversion γR
a , or low search cost ca, all
relative to the asset market ineﬃciency η, that is, if
γR
a ca
Wa
= γaca ≤1
2η.
(24)
Otherwise, the investor should invest as uninformed.
This result is intuitive and consistent with the idea that active investors should be those
who have a comparative advantage in asset allocation — large investors who can hire a
serious manager-selection team or sophisticated investors with special insights on asset man-
agers.
For such agents, the cost of ﬁnding and vetting an informed asset manager is a
smaller fraction of their investment, as captured by equation (24). In contrast, small retail
investors are better served by low-cost uninformed investing. The next proposition states
15Wealth levels vary a lot more in the cross-section — easily by factors measured in thousands — than
relative risk aversions, so variation in γa is mostly driven by wealth diﬀerences in the real world.
16These independence assumptions only aﬀect our performance results, and the results would only be
strengthened under the realistic assumption that high sophistication (low c) correlates with high wealth W,
or if noise allocators are more likely to have low sophistication and wealth.
29


<!-- PAGE 33 -->

the corresponding result for asset managers.
Proposition 6 (Which managers should be informed?): Asset manager m should acquire
information if her information cost is low, km ≤kM; otherwise, the manager should remain
uninformed.
Clearly, asset managers are more likely to have success in informed trading if they are
well educated, experienced, and have access to an existing research infrastructure, while
managers who ﬁnd it more diﬃcult to collect useful information might prefer to limit their
costs.
B.
How Size and Sophistication Aﬀect Performance
The model makes clear predictions about the expected performance diﬀerences across
diﬀerent types of investors and asset managers. Investors who are more wealthy (high Wa)
and more sophisticated (low ca) are more likely to search for an informed manager, and thus
such investors allocate to better managers on average.
To state these performance predictions in terms of percentage returns, we suppose, with-
out loss of generality, that a manager scales the portfolio such that any investor with a
relative risk aversion of γR
a = ¯γR optimally invests his entire wealth Wa with the manager.
We can then deﬁne the investor’s return with the manager as his dollar proﬁt per capital
committed Wa. An investor with relative risk aversion twice as high, γR
a = 2¯γR, naturally
invests only half his wealth with the manager and earns the same percentage return (before
fees) on the committed capital.
Proposition 7 (Investor performance — size and sophistication): Holding ﬁxed other char-
acteristics, larger investors (higher Wa) earn higher expected returns before and after fees
and pay lower percentage fees, on average. Likewise, holding ﬁxed other characteristics, more
sophisticated investors (lower ca) earn higher expected returns before and after fees and pay
lower percentage fees.
These results are intuitive and give rise to several testable predictions that we confront
30


<!-- PAGE 34 -->

with existing evidence in Section V. Since large and sophisticated investors can better aﬀord
to spend resources on ﬁnding an informed manager, they are more likely to ﬁnd one and,
as a result, expect to earn higher returns.17 The higher returns represent compensation for
the search costs that these investors incur, but they can even outperform after search costs
when inequality (24) is strict.
Said diﬀerently, if a small investor with no special knowledge of asset managers (that is,
an investor for whom (24) is not satisﬁed) invests with an active manager, then he must be a
noise allocator. Since noise allocators pay fees even to uninformed managers, such investors
are expected to earn lower returns.
On the other hand, noise allocators are underrepresented among large sophisticated in-
vestors. We note that the model-implied eﬀect is not linear in that, as investors become very
large (or sophisticated), they search for a manager almost surely and therefore even larger
size has a negligible eﬀect on their expected performance. We next consider how performance
varies across asset managers.
Proposition 8 (Asset manager performance):
(i) Asset manager returns (before and after fees) and their average investor size covary
positively. Similarly, returns and average sophistication covary positively.
(ii) Asset manager size and expected returns (before and after fees) covary positively. Sim-
ilarly, managers with a comparative advantage in collecting information (km ≤kM)
earn higher expected returns before and after fees.
Part (i) shows that asset managers with larger and more sophisticated investors are
more likely to have investors who have performed due diligence and conﬁrmed that they
are informed about security markets. These managers, being more likely to have passed a
screening, should deliver higher expected returns on average (even though some of them can
still be uninformed as some large investors can also be noise allocators). Other measures
17The fact that investors with large absolute risk tolerance choose informed investing through managers
(by paying search costs and fees) parallels the result of Verrecchia (1982) that more risk-tolerant investors
purchase more precise (and expensive) signals.
31


<!-- PAGE 35 -->

Sophisticated
investors
Good
securities
Bad
securities
Noise
allocators
Good asset
managers
Bad asset
managers
Figure 5:
Testing the model at three levels. The ﬁgure illustrates stylistically the
three layers for which our model has new cross-sectional implications: investors, asset man-
agers, and ﬁnancial markets. Further, the model also makes predictions on the interaction
between these layers, that is, the interaction between investors, securities, and the industrial
organization of asset management.
that proxy for the type of a manager’s clientele, such as the proportion of large investors
(i.e., with wealth above a given threshold), would work as well.
Part (ii) shows that managers who ﬁnd it easier to collect information are more likely to
do so. Indeed, for the marginal manager, the cost of information equals the beneﬁt, so those
with higher costs will not acquire information. Hence, an asset manager may be more likely
to be informed if she is well educated, experienced, and beneﬁts from ﬁrm-wide investment
research as part of an investment ﬁrm with multiple funds. Investors’ search process may
therefore consist in part of examining whether an asset manager has such qualities, as we
discuss further in Appendix B.
V.
Empirical Implications
Our model has implications for investors, asset managers, and ﬁnancial markets — three
layers that we represent schematically in Figure 5. We start by examining the predictions
and empirical evidence at the middle level, that is, concerning managers.
32


<!-- PAGE 36 -->

A.
Performance of Asset Managers
The central prediction of asset market eﬃciency is that managers underperform by an
amount equal to their fees.
Indeed, early empirical literature documents negative aver-
age after-fee returns for U.S. mutual funds (Fama (1970)). More recent evidence suggests
that the average alpha after fees is close to zero (Berk and Binsbergen (2015)). Further, a
growing body research shows that evidence for the average asset manager hides signiﬁcant
cross-sectional variation across managers.
Indeed, the literature documents a signiﬁcant
diﬀerence between the net-of-fee performance of the best and worst managers of mutual
funds (Kosowski, Timmermann, Wermers, and White (2006), Kacperczyk, Sialm, and Zheng
(2008), Fama and French (2010), Keswani, Ferreira, Miguel, and Ramos (2016)), hedge funds
(Kosowski, Naik, and Teo (2007), Fung, Hsieh, Naik, and Ramadorai (2008), Jagannathan,
Malakhov, and Novikov (2010)), private equity, and venture capital funds (Kaplan and
Schoar (2005)). For instance, Kosowski, Naik, and Teo (2007) report that “top hedge fund
performance cannot be explained by luck, and hedge fund performance persists at annual
horizons... Our results are robust and relevant to investors as they are neither conﬁned to
small funds, nor driven by incubation bias, backﬁll bias, or serial correlation.”
The strong performance of the best managers is a rejection of Eugene Fama’s hypothesis
that asset markets are fully eﬃcient and all asset managers underperform by their fees.
Further, the net-of-fee performance spread between the best and worst managers is a rejection
of the Berk and Green (2004) hypothesis that all managers deliver the same expected net-
of-fee return.
The existence of the performance spread, however, is consistent with our
model’s predictions. In our model, top asset managers should be diﬃcult to locate and their
outperformance must compensate investors for their search costs.
We note the following subtlety concerning the relation between our model and empirical
tests. Our model implies that investors should be able to ﬁnd managers that outperform net
of fees only after incurring a search cost, but does this then imply that an empirical researcher
should be able to identify such managers? On the one hand, researchers should not be able
to locate informed managers based on public information that investors can easily process
33


<!-- PAGE 37 -->

(as seen in the version of our model in which investors can search for free based on AUM; see
Section III.A.1). On the other hand, skilled researchers using large commercial databases
and advanced statistical methods should be able to locate informed managers, to the extent
that this research mimics investors’ costly search process. Of course, investors with access
to more data (e.g., meetings with managers that reveal the trading infrastructure) should
be able to do even better.
Again, there is a close parallel between the market for assets and the market for asset
management: Just like ﬁnding good asset managers should be diﬃcult but not impossible,
ﬁnding good securities should be diﬃcult but not impossible. In both cases, researchers may
identify good managers and good securities based on commercial data that are costly to
process. Asset pricing anomalies, for instance, are typically based on such commercial data.
B.
Manager Performance: Link to Our Search Mechanism
While the existence of a performance spread among the best and worst asset managers
rejects existing theories and favors ours, this “victory” may not necessarily be informative
given that other theories might also predict such a performance spread. To test the model
at a deeper level, we examine whether performance diﬀerences appear to be driven by our
search mechanism, that is, are consistent with the predictions of Proposition 8.
Consistent with search costs being higher for alternative investments (hedge funds and
private equity) than for mutual funds, we see larger performance spreads among alternative
managers. However, comparisons across markets may be driven by multiple diﬀerences, and
thus we dig deeper still, in Table I.
A number of prior papers provide signiﬁcant and diverse evidence for the model’s perfor-
mance predictions. First, Evans and Fahlenbrach (2012) ﬁnd that mutual funds that have
an institutional share class outperform other mutual funds, consistent with the idea that
institutional investors are more likely to have performed due diligence (Proposition 8(i)).
Second, the group of managers servicing all institutional investors outperform the mutual
funds servicing retail investors (Gerakos, Linnainmaa, and Morse (2016)). Indeed, Gerakos,
34


<!-- PAGE 38 -->

Linnainmaa, and Morse (2016) ﬁnd that the asset managers servicing institutions deliver
outperformance after fees, in contrast to the evidence on the average retail mutual fund
discussed above.
Third, Guercio and Reuter (2014) ﬁnd that mutual funds sold directly to searching in-
vestors outperform those that are placed via brokers who earn commissions or loads (to noise
allocators).
Fourth, consistent with Proposition 8(ii), Chevalier and Ellison (1999) ﬁnd that “man-
agers who attended higher-SAT undergraduate institutions have systematically higher risk-
adjusted excess returns’’ and Chen, Hong, Huang, and Kubik (2004) ﬁnd that “Controlling
for fund size [...] the assets under management of the other funds in the family that the fund
belongs to actually increase the fund’s performance.”
Last, consistent with Proposition 1(ii), the outperformance of managers of searching
investors is larger in less eﬃcient markets. Dyck, Lins, and Pomorski (2013), for instance,
ﬁnd that “active management in emerging market equity outperforms passive strategies by
more than 180 bps per year, and that this outperformance generally remains signiﬁcant when
controlling for risk through a variety of mechanisms. In EAFE equities (developed markets
of Europe, Australasia, and the Far East), active management also outperforms, but only
by about 50 bps per year, consistent with these markets being relatively more competitive
and eﬃcient.”
From investors’ perspective, the relevant measure of manager performance is average
excess return (or alpha), but when evaluating managers’ skill per se, Berk and Binsbergen
(2015) argue that the manager’s “value added” is a better measure. They ﬁnd that the “cross-
sectional distribution of managerial skill is predominantly reﬂected in the cross-sectional
distribution of fund size,” a result consistent with the prediction of our Proposition 8(ii).
C.
Investor Performance: Link to Our Search Mechanism
We now turn to the predictions for the top layer of Figure 5, namely, investors. We have
already discussed that institutional investors outperform even after fees (Gerakos, Linnain-
35


<!-- PAGE 39 -->

Table I: Evidence on our predictions. Panel A includes references on the performance
diﬀerences between asset managers servicing investors who are more likely to be searching
investors vs.
those servicing noise allocators.
Panel B includes quotes on the investors’
performance. These references show that asset managers found by searching investors out-
perform those of noise allocators, consistent with our model’s predictions.
36


<!-- PAGE 40 -->

maa, and Morse (2016)), and hence perform better than the overall group of retail investors
in their active mutual fund allocations. This mirror image of the result for asset managers
is consistent with Proposition 7.
Further, as seen in Panel B of Table I, Dyck and Pomorski (2016) ﬁnd that large insti-
tutions outperform small ones in their private equity investments, which further supports
Proposition 7. Moreover, consistent with our model’s implication that size only matters up
to a certain point (at which all investors decide to search), Dyck and Pomorski (2016) ﬁnd
a non-linear eﬀect of size that eventually diminishes.
Likewise, funds of hedge funds perform better on their local investments where they likely
have a search advantage (Sialm, Sun, and Zheng (2014)), which supports a diﬀerent aspect
of Proposition 7.
Lastly, Gerakos, Linnainmaa, and Morse (2016) ﬁnd that larger investors pay lower per-
centage fees than small investors with the same asset manager, also consistent with Propo-
sition 7. This means that larger investors beneﬁt more from active investing both because
they pay lower fees and because their search costs are a smaller fraction of assets. We note
that this empirical ﬁnding constitutes an even simpler rejection of Berk and Green (2004):
if investors pay diﬀerent fees in the same fund, then surely not all investors can earn a zero
expected alpha after fees.
D.
Implications for Asset Pricing and Market Eﬃciency
Turning to the bottom layer of Figure 5, consider the implications for capital markets.
Our model is consistent with the existence of anomalies reﬂecting the types of strategies
that informed managers pursue.18 Given that other theories also may explain anomalies,
we need to test the theory at a deeper level. Eﬃciently ineﬃcient markets means that the
marginal investor should be indiﬀerent between uninformed investing and searching for asset
managers, where the latter should deliver an expected outperformance balanced by asset
18While the eﬃcient market hypothesis is a powerful theory, it is nevertheless diﬃcult to test because of
the so-called “joint hypothesis” problem. However, the many documented violations of the Law of One Price
(securities with the same cash ﬂows that trade at diﬀerent prices) constitute a clear rejection of fully eﬃcient
asset markets.
37


<!-- PAGE 41 -->

management fees and search costs, consistent with the ﬁndings of Gerakos, Linnainmaa, and
Morse (2016) for professional asset managers. Section III.C delivers additional predictions
on the magnitude of the ineﬃciency, which are yet to be tested.
Further, in an eﬃciently ineﬃcient market, anomalies are more likely to arise the more
resources a manager needs to trade against them (higher k) and the more diﬃcult it is for
investors to build trust in such managers (higher c). For instance, while convertible bond
arbitrage is a relatively straightforward trade for an asset manager (low k), it might have
performed well for a long time because it is diﬃcult for investors to assess (high c).
E.
Industrial Organization of Asset Management
Returns to Scale. In our model, the overall asset management industry faces decreasing
returns to scale, as a larger amount of capital with informed managers (I) leads to more eﬃ-
cient markets (lower η), which reduces manager performance. This implication is consistent
with the evidence of Pastor, Stambaugh, and Taylor (2015).
Individual managers in our model, however, do not face decreasing returns to scale (con-
trolling for industry size), and indeed larger managers are better on average (because search-
ing investors look for informed managers).
This implication is consistent with Ferreira,
Keswani, Miguel, and Ramos (2013), who ﬁnd that larger asset managers perform better.19
In contrast, Berk and Green (2004) assume that individual managers face decreasing
returns to scale (e.g., due to transaction costs). Pastor, Stambaugh, and Taylor (2015) study
what happens when a given manager grows larger (seeking to eliminate the eﬀect that larger
managers may be diﬀerent, cross-sectionally) and ﬁnd that “all methods considered indicate
decreasing returns, though estimates that avoid econometric biases are insigniﬁcant.”
Industry Size. Our model has several implications for the size of the asset management
industry. The asset management industry grows when investors’ search costs decrease or
when asset managers’ information costs go down, leading to more eﬃcient asset markets.
19In the U.S., managers with larger fund family size perform better, but the size of the speciﬁc fund is
a negative predictor. Outside the U.S., both the fund and the fund family size predict returns positively.
Since information costs may be more related to the size of the fund family (i.e., the overall asset management
ﬁrm), it makes sense that family size appears to be the more robust predictor.
38


<!-- PAGE 42 -->

This phenomenon is consistent with the evidence of Pastor, Stambaugh, and Taylor (2015).
Other important models that speak to the size of the asset management industry include
Berk and Green (2004), Garc´ıa and Vanden (2009), and Pastor and Stambaugh (2012).
Concentration. When investors’ search costs go down, our model predicts that the number of
managers will fall, but the remaining managers will be larger (indeed, so much larger that the
total size of the asset management industry grows as mentioned above). Such consolidation
of the asset management industry is discussed in the press, but we are not aware of a direct
test of this model prediction.
Fees. Finally, we have predictions for asset management fees. Asset management fees should
be larger for managers of more ineﬃcient assets and in more ineﬃcient asset management
markets. For instance, if search costs for managers are large, this leads to less active investing
and higher management fees. Note that the higher management fee in this example is not
driven by higher information costs for managers, but rather by the equilibrium dynamics
between the markets for the asset and asset management. This may help explain why hedge
funds have historically charged higher fees than mutual funds. Also, markets for assets that
are costly to study should be more ineﬃcient and have higher management fees. This can
help explain why equity funds tend to have higher fees than bond funds and why global
equity funds have higher fees than domestic ones. Lastly, in a cross-country study, Khorana,
Servaes, and Tufano (2008) ﬁnd that mutual fund “fees are lower in wealthier countries with
more educated populations,’’ which may be related to lower search frictions for well-educated
investors.
VI.
Conclusion
We propose a theory of investors searching for informed asset managers — in short,
Grossman-Stiglitz with asset management. The theory captures the time-consuming vetting
process through which real-world investors examine an asset manager (portfolio construction,
number of employees, professional pedigree, whether the manager operates a trading desk
24/7, co-location on major trading venues, costly information sources, risk management,
39


<!-- PAGE 43 -->

valuation methods, ﬁnancial auditors, and so on) and the costly process through which an
asset manager examines a security. Our search-plus-information model turns out to be highly
tractable and yields several novel results that help explain numerous empirical facts about
asset prices and asset management that are puzzling in light of existing theories.
40


<!-- PAGE 44 -->

Appendix A.
Further Analysis and Proofs
A.1.
Equilibrium characterization: interior and corner equilibria.
Here we collect the conditions that deﬁne an equilibrium of the four endogenous variables
(p, f, M, A). First, the price p and the corresponding market ineﬃciency η are given by (9)
as a function of the other endogenous variables. Second, the fee f depends on an investor’s
best outside option, which is the larger of the ex-ante utility of investing on one’s own (given
by uu) and that from searching for another manager (given by ui −c −f). It follows that
f = min
 η
2γ , c

.
(A1)
We have the following types of equilibria (where p and f are given above).
Interior Equilibrium: Any pair (M, A) ∈[0, ¯
M] × [0, ¯A] satisfying equations (14) and (15)
constitutes an interior equilibrium.
Corner at Zero: The trivial outcome (M, A) = (0, 0) is always an equilibrium. If, for all
(M, A) > (0, 0), f(M, A)A < kM or c(M, A) > ui −uu = η
γ, then (M, A) = (0, 0) is the only
equilibrium.
Nonzero Corner: The pair (M, A) ∈[0, ¯
M] × [0, ¯A] is an equilibrium if and only if
η(I)
2γ
≥c (M, A) ,
 η
2γ −c

( ¯A −A) = 0
(A2)
c (M, A) A ≥kM,
(cA −kM)( ¯
M −M) = 0.
(A3)
Conditions (A2)–(A3) encompass the conditions for an interior equilibrium as well, but
also allows for the corner solutions A = ¯A and M = ¯
M. Here, (A2) states that investors’
utility from searching must be at least as high as their utility from not searching, with equality
holding unless everyone searches (“complementary slackness”). Similarly, (A3) states that
managers must expect nonzero proﬁt from becoming informed and must be indiﬀerent unless
all managers become informed.
A.2.
Equilibrium when Investors Can Search Based on AUM
Here we outline the analysis of the model that incorporates a third investment option,
namely searching for a random manager based on AUM. In this case, investors can invest
either (i) as uninformed with no fees or search costs; (ii) with a manager who is surely
informed by paying an asset management fee and a search cost; or (iii) with a random
manager by paying an asset management fee but no search cost.
We model the third investment option as follows. An investor who performs a random
search has a probability of drawing an informed manager, denoted by pI, equal to the
41


<!-- PAGE 45 -->

proportion of the total AUM (or the proportion of investors) with informed managers:
pI = A + N M
¯
M
A + N .
(A4)
Note that looking at the number of investors and looking at AUM are equivalent since all
investors invest the same dollar amount with the chosen manager — informed managers use
higher leverage (hold less cash) on average than uninformed ones, but the AUM accounted
for by an investor is the same. (This statement is modiﬁed accordingly if agents’ size or risk
aversion diﬀer, as we consider in Section IV.B and in Appendix A.3 below.)
The random search mechanism makes use of AUM information (since the numerator in
the deﬁnition of pI is the number of investors with informed managers and the denominator
is the total number of investors) and this AUM information is beneﬁcial in the sense that the
success probability pI is larger than the chance of ﬁnding an informed manager by picking
completely randomly among all managers, M/ ¯
M. There are several interpretations of this
AUM-based search. In particular, it can be viewed as (a) copying a random investor (who
may be informed or a noise allocator, so even such a random investor’s allocation contains
some information), (b) an investment in the “market portfolio” of all asset managers (in this
case, pI is the fraction of capital invested with informed managers rather than a probability),
or (c) another mechanism through which investors use freely available information to pick a
manager.20
Let R > 0 denote the mass of investors searching randomly, and note that an equilibrium
now consists of a collection of ﬁve endogenous variables (p, f, M, A, R). As before, the price
p and the corresponding market ineﬃciency η are given by (9) as functions of the other
endogenous variables, but now the number of informed investors I also depends on R:
I = A + RpI + N M
¯
M .
(A5)
Next, the fee f is determined via bargaining as before. It is helpful to introduce notation
for the ex-ante utilities of the diﬀerent types of investors. The ex-ante utility of paying a
search cost to be sure to ﬁnd an informed manager is denoted by Ui = ui −c −f and the
ex-ante utility of uninformed investors is Uu = uu. Turning to the new part, the ex-ante
utility of investors searching randomly based on AUM is
Ur = pI(ui −f) + (1 −pI)(uu −f) = pIui + (1 −pI)uu −f,
(A6)
where we employ a ﬁrst-order approximation for simplicity (see footnote 20).
20 These diﬀerent interpretations have slightly diﬀerent associated utilities (because of the diﬀerence be-
tween investing with a single manager who is informed with probability pI versus investing with many
managers of which the fraction pI is informed), but their utilities are the same to the ﬁrst-order approx-
imation. We present our results based on the simple expression (A6), but the only consequence of this
assumption is the speciﬁc form of equations (A8), (A12) and (A16); all qualitative implications are the
same.
42


<!-- PAGE 46 -->

To calculate the fee, the investor’s outside option is now the best of his three options,
that is, its value equals max{Uu, Ui, Ur}. In any equilibrium, it cannot be the case that
Ur > Ui, and thus we can focus on max{Uu, Ui}, which yields (A1) just as before.
The following optimality conditions for investors determine A and R. First, for search to
be optimal, we must have Ui ≥Uu, that is, as before,21
η(I)
2γ
≥c (M, A) ,
(A7)
which holds with equality if there are uninformed investors, A + R < ¯A.
Similarly, for
random search to be optimal, we must have Ur = Ui, that is,
pIui + (1 −pI)uu −f = ui −c −f,
(A8)
which can be shown to be equivalent to
(1 −pI)η
γ = c.
(A9)
Finally, managers’ optimality condition is now more complex. In particular, indiﬀerence
between being informed and not means
1
M (A + RpI) c −k =
1
¯
M −M R(1 −pI)c,
(A10)
where the left-hand side represents the fee revenue of an informed manager, net of the cost
of becoming informed, and the right-hand side represents the fee revenue of an uninformed
manager. As before, the fees paid by noise allocators are not included, as they do not depend
on manager type. Using the deﬁnition of pI, the indiﬀerence condition simpliﬁes to
cA

1 +
R
A + N

= kM.
(A11)
To summarize, equilibrium with random search is characterized as follows (where, as
before, p and f are given by the other endogenous variables).
Interior Equilibrium: The tuple (M, A, R) ∈R3
+ is an interior equilibrium if M ≤
¯
M,
A + R ≤¯A, and indiﬀerence conditions apply to investors (Uu = Ui = Ur) and managers:
η
2γ = c = (1−pI)η
γ
(A12)
cA

1 +
R
A + N

= kM.
(A13)
21Note that in any nontrivial equilibrium it cannot be the case that Uu > Ui, because then there would
be no informed investors and in turn no informed managers, meaning pI = 0 and therefore R = 0.
43


<!-- PAGE 47 -->

Corner at Zero: The trivial outcome A = R = M = 0 is always an equilibrium. If, for all
(M, A, R) with M > 0, fA < Mk or c > ui −uu = η
γ, then (M, A, R) = (0, 0, 0) is the only
equilibrium.
Nonzero Corner The tuple (M, A, R) ∈R3
+ \ {(0, 0, 0)} is an equilibrium if and only if
M ≤¯
M, A + R ≤¯A, and
η
2γ ≥c,
 η
2γ −c

( ¯A −A −R) = 0
(A14)
cA

1 +
R
A + N

≥kM,

cA

1 +
R
A + N

−kM

( ¯
M −M) = 0
(A15)
(1 −pI)η
γ ≥c,

(1 −pI)η
γ −c

R = 0.
(A16)
As before, we see that there can be interior equilibria and corner equilibria. In an interior
equilibrium, investors are indiﬀerent between their three options (uninformed investing, pay-
ing for search, random search). In this case, agents who search randomly neither overperform
nor underperform, in the language of Proposition 1. We also note that (A12) implies that
pI = 1
2 in an interior equilibrium.
The set of corner equilibria is more complex now as there are more endogenous vari-
ables. In one set of such equilibria, random search does not occur. In particular, consider
any equilibrium without the random search option. Such an equilibrium continues to be an
equilibrium in the model that allows random search if and only if Ur ≤max(Uu, Ui). Another
type of corner equilibrium involves a positive number of investors searching at a cost, a posi-
tive number of investors searching randomly, but no investor choosing uninformed investing,
that is, A > 0, R > 0, and ¯A −A −R = 0.
A.3.
Equilibrium with Small and Large Investors and Asset Managers
Here we show how to derive an equilibrium with heterogeneous agents, but ﬁrst we com-
ment on the statistical structure of (ca, γR
a , Wa), beyond the independence already assumed.
While γR
a and Wa are scalars, and therefore straightforward to specify, the costs ca are less
straightforward since they are functions. We could consider a number of choices, including
(i) ca scalars (constant functions), (ii) ca proportional to c0 for all a, or (iii) ca in some gen-
eral continuous-function space, possibly one in which all elements are ordered (and thus the
functions do not cross). The results in Section IV, though, hold for any general speciﬁcation
once an equilibrium is ﬁxed.
An equilibrium with heterogeneous agents consists of a price p, a fee fa for each investor
a, a set of active investors, and a set of informed managers. We show that the equilibrium
has the following form. First, the set of managers is {m : km ≤kM} = [0, M], which is
naturally characterized by the total number of informed managers M (as before).
44


<!-- PAGE 48 -->

Second, for any investor a, market ineﬃciency η is a given quantity. The same argument
as above (see Section A.1), reﬁned to take the agent’s characteristics into account, leads to
fa = min
 η
2γa
, ca

.
(A17)
In equilibrium, agent a searches for a manager if and only if ua,u ≤ua,i −ca −fa, so that the
only observed fee is fa = ca. The condition for searching then becomes 2ca ≤ua,i −ua,u, or
γaca ≤1
2η. Hence, the set of active investors is {a : γaca ≤1
2η}, where the price ineﬃciency
η is part of the equilibrium. As for the agent’s risky investment, it is the same as that of an
agent with unit risk tolerance, but multiplied by her own risk tolerance 1/γa.
As before, the price can be characterized via the price eﬃciency η. The price eﬃciency
depends on the aggregate risk tolerance of all investors with informed managers,
τ = ¯A E
 1
γa
1{γaca≤1
2 η}

+ N M
¯
M E
 1
γn

.
(A18)
Here, the ﬁrst term is the total risk tolerance of searching investors (those who decide to
search based on (24)), and the second term is the total risk tolerance of the noise allocators
who happen to ﬁnd an informed manager. Given the total risk-bearing capacity of investors
with informed managers, equation (9), which determines price ineﬃciency η, is modiﬁed by
replacing I/γ with τ:
η(τ) = −1
2 log

1 −
σ2
qσ2
ε
τ 2 + σ2
qσ2
ε
σ2
v
σ2
ε + σ2
v

.
(A19)
Finally, the indiﬀerence condition for the marginal asset manager M is that the fee
revenue from searching investors per manager covers her cost kM:
¯A
M E

ca 1{γaca≤1
2 η}

= kM.
(A20)
Hence, a general equilibrium with many types of investors and managers is characterized by
(η, τ, M) that satisfy (A18)–(A20).22
A.4.
Endogenizing Noise Allocators
The behavior of, and fee paid by, noise allocators can be derived as an outcome by
incorporating the following two features into the model. First, noise allocators use a poor
search technology: they pay the cost c to be matched with a manager, but they ﬁnd a
random manager, not necessarily an informed one (they draw the manager from the uniform
22While the indiﬀerence condition (A20) applies with equality in an interior equilibrium, corner solutions
are characterized by either M = 0 and the right-hand side being greater or M = ¯
M and the left-hand side
being greater.
45


<!-- PAGE 49 -->

distribution, not one given by AUM). Second, noise allocators face a high cost cu of investing
on their own even without information, a cost so high that they always search for a manager.
Our results do not depend on whether noise allocators believe that the manager is informed
or not, so noise allocators can be viewed as fully rational or biased. Our assumptions can
be seen as capturing the idea that noise allocators invest based on trust as proposed by
Gennaioli, Shleifer, and Vishny (2015). We note that by taking a ﬁxed number of noise
allocators, we rule out the possibility that managers exploit behavioral biases to aﬀect the
number of noise allocators.
Since noise allocators face a high cost of investing on their own, they all search for an
asset manager. A fraction M/ ¯
M randomly ﬁnd an informed manager while the rest ﬁnd
uninformed managers. Since noise allocators cannot tell the diﬀerence between informed
and uninformed managers, they pay the same fee either way. The speciﬁc fee that they pay
is not central to our results, but we can model the bargaining as before: noise allocators
receive a utility from investing with a random active manager that we denote by un. Given
the unattractive option of investing on their own, noise allocators’ alternative to investing
with the current manager is paying the cost c again to ﬁnd another manager and investing
with him at an expected fee of ¯f. The gains from agreeing to pay the current manager a fee
of f is therefore W + un −c −f −(W + un −2c −¯f) = c + ¯f −f.
The manager has a gain from agreement of f, so the equilibrium fee maximizes (c+ ¯f−f)f,
which under ¯f = f gives f = c. As seen from (11) and (14), the fee paid by noise allocators
is the same as the fee paid by other investors in an interior equilibrium.
A.5.
Partial Asset-Market Equilibrium
Here we outline the derivation of the asset market equilibrium of Section II.A in the
interest of being self-contained, although these results are eﬀectively provided in Grossman
and Stiglitz (1980). An agent having conditional expectation of the ﬁnal value µ and variance
V optimally demands a number of shares equal to
x = µ −p
γV .
(A21)
To compute the relevant expectations and variance, we conjecture the form (6) for the price
and introduce a slightly simpler “auxilary” price, ˆp = v −¯v + ε −θq(q −¯q), with the same
46


<!-- PAGE 50 -->

information content as p:
E[v|p] = E[v|ˆp] = ¯v + βv,ˆpˆp = ¯v +
σ2
v
σ2
v + σ2
ε + θ2
qσ2
q
ˆp
(A22)
E[v|s] = E[v|v + ε] = ¯v + βv,s(s −¯v) = ¯v +
σ2
v
σ2
v + σ2
ε
(s −¯v)
(A23)
var(v|p) = var(v|ˆp) = σ2
v −
σ4
v
σ2
v + σ2
ε + θ2
qσ2
q
= σ2
v
 σ2
ε + θ2
qσ2
q

σ2
v + σ2
ε + θ2
qσ2
q
(A24)
var(v|s) = σ2
v −
σ4
v
σ2
v + σ2
ε
=
σ2
vσ2
ε
σ2
v + σ2
ε
.
(A25)
We can now insert these demands into the market-clearing condition (5), which is a linear
equation in the random variables q and s. Given that this equation must hold for all values
of q and s, the aggregate coeﬃcients on these variables must equal zero, and similarly, the
constant term must be zero. Solving these three equations leads to the coeﬃcients in the
price function (6) given by
θ0 = ¯v −
γ¯q var(v|s)
I + ( ¯A + N −I) var(v|s)
var(v|p)
(A26)
θs =
I
σ2
v
σ2v+σ2ε + ( ¯A + N −I) var(v|s)
var(v|p)
σ2
v
σ2v+σ2ε+θ2qσ2q
I + ( ¯A + N −I) var(v|s)
var(v|p)
(A27)
θq = γ σ2
ε
I .
(A28)
Hence, by construction, a linear equilibrium exists.
To compute the relative utility, we start by noting that, with a ∈{u, i},
e−γua = E

e−1
2
(µa−p)2
Va

,
(A29)
where µa and Va are the conditional mean and variance of v for an investor of type a.
To complete the proof, one uses the fact that, for any normally distributed random variable
z ∼N (µz, Vz), it holds that (e.g., based on the moment-generating function of the noncentral
chi-square)
E
h
e−1
2 z2i
= (1 + Vz)−1
2 e−1
2
µ2z
1+Vz ,
47


<!-- PAGE 51 -->

and performing the necessary calculations gives
uu = 1
γ log
σv−p
σv|p

+ 1
2γ
(¯v −θ0)2
σ2
v−p
(A30)
ui = 1
γ log
σv−p
σv|s

+ 1
2γ
(¯v −θ0)2
σ2
v−p
.
(A31)
(We note that the last term,
1
2γ
(¯v−θ0)2
σ2
v−p , represents the utility attainable by an agent who
cannot condition on the price.)
By combining (A30), (A31), and the deﬁnition of η, we see that (8) holds. To see (9),
we use (A24), (A25), and the expression (A28) for θq.
A.6.
Proofs
Before continuing with the proofs of the next propositions, we state an auxiliary result
regarding the number of managers. First, let the unique value of M that solves managers’
indiﬀerence condition (15) for any I be given by
M(I) = min
(
η(I)I
2γk + η(I) N
¯
M
, ¯
M
)
,
(A32)
where we use the fact that I = A + N M
¯
M . Given this deﬁnition, the number of managers
depends on I as follows.
Lemma 1: The function of I given by Iη(I) increases up to a point ¯I and then decreases,
converging to zero. Consequently, M(I) increases with I for I low enough, and decreases
towards zero as I tends to inﬁnity.
Proof of Lemma 1:
The function x →xη(x) is a constant multiple of
h(x) := x log
a + x2
b + x2

,
(A33)
with a > b > 0. Its derivative equals
h′(x) = log
a + x2
b + x2

+ xb + x2
a + x2
2x(b + x2) −2x(a + x2)
(b + x2)2
= log
a + x2
b + x2

−
2(a −b)x2
(a + x2) (b + x2).
For x = 0, the ﬁrst term is clearly higher: h′(0) > 0. For x →∞, the second is larger,
so that lim h′(x) < 0. Finally, letting y = x2 and diﬀerentiating h′(y) with respect to y one
48


<!-- PAGE 52 -->

sees that h′′(y) = 0 when y satisﬁes the quadratic
y2 −(a + b)y −3ab = 0,
(A34)
which clearly has a root of each sign. Thus, since y = x2 is always positive, h′′(x) changes
sign only once. Given that h′(x) starts positive and ends negative and its derivative changes
sign only once, we see that h′ itself must change sign exactly once. This result means that
h is hump-shaped. Finally, we can apply L’Hˆopital’s rule to h(x) = log

a+x2
b+x2

/(1/x) to
conclude that limx→∞h(x) = 0.
To make a statement about the number of informed managers M, we use (A32) and the
ﬁrst result.
Proof of Propositions 1 and 1’:
Part (i): The statement about informed managers follows
from the fact that investors matched with good managers rationally choose to pay the fee and
invest with the manager rather than invest as uninformed. The statement about uninformed
managers follows from the facts that uninformed managers do not provide any investment
value and that their fee is strictly positive. Part (ii) is the indiﬀerence condition for active
investors and we note that the outperformance ui −f −uu = c is clearly larger if the
equilibrium c is larger. Part (iii) follows from expressing the aggregate outperformance as

A + N M
¯
M

(ui −f −uu) + N

1 −M
¯
M

(−f) = Af −N

1 −2M
¯
M

f ,
(A35)
using that ui−uu = η
γ = 2f. This outperformance is positive if and only if N
 1 −2M
¯
M

≤A.
Finally, an interior equilibrium in the context of Proposition 1b means that Ur = Uu = Ui.
The ﬁrst equality is literally the conclusion of the proposition. It is captured mathematically
in our description of an equilibrium by equation (A12), taking into account the equivalence
between (A8), which encodes Ur = Ui, and (A9), combined with the fact that Ui = Uu is
equivalent to (12) (given that (12) holds with equality in an interior equilibrium).
Proof of Proposition 2:
(i) Consider the largest I equilibrium under the search cost c1,
denoted using the subscript 1. We show that, under c2, an equilibrium exists with larger I.
To see this, note that since (14) holds with equality for c1, we have η(I1) ≥2γc2(M1, A1).
Consider now the set

I | I ≥I1, I −M(I) N
¯
M ≤¯A

,
(A36)
where I −M(I) N
¯
M is the number of searching investors A corresponding to I. This set is not
empty because it includes I1. Either η(I) > 2γc2
 M(I), I −M(I) N
¯
M

over the entire set, in
which case A = ¯A corresponds to an equilibrium for c2, or η(I) = 2γc2
 M(I), I −M(I) N
¯
M

for a value I2 ≥I1, which is the desired conclusion.
The asset market eﬃciency and fee are determined monotonically by the level of I. The
49


<!-- PAGE 53 -->

number M of managers can either increase or decrease given the result on the shape of M.
Finally, if M(I2) ≤M(I1), then A2 ≥A1 from A = I −M N
¯
M . If M(I2) ≥M(I1), then
the same conclusion follows from (15).
(ii) Since the functions cj are continuous on [0, ¯A] × [M0, ¯
M] for any M0 > 0, they
converge to zero uniformly on this compact set. Pick M0 low enough so that M(I) > M0
for any I ∈[ ¯A, ¯A + N].
Since η is bounded away from zero on the set of interest, for high enough j there is an
equilibrium with A = ¯A. By letting ¯Aj →∞, the equilibrium value Aj goes to ∞. Hence,
the market converges toward full eﬃciency in the limit.
Proof of Proposition 3:
We note that cA ≥0 ensures that equation (14) deﬁnes a function
A(M) associating each value M with a unique value of A. Further, adding the condition
cM ≤0 implies that I(M) ≡A(M) + M N
¯
M increases strictly with M.
One can describe the eﬀect of k using the language of graphs. (A more rigorous argument
can be made following similar logic to that in the proof of Proposition 2.) At the highest I,
the increasing function I−1 crosses M from below; since a lower value of k translates into
an upward shift of the function M, there exists at least one equilibrium at the new k with
a higher value of I than before. Since I does not vary with k and it is increasing, M also
increases. The ineﬃciency η decreases as I increases.
The level of A, in contrast, can either increase or decrease. To see the latter fact, imagine
a function c that increases abruptly in A around the original equilibrium, but is ﬂat with
respect to M. Since η decreases, A has to decrease from (14). Formally, make use of
dη
dk = cM
dM
dk + cA
dA
dk .
(A37)
Proof of Proposition 4:
Letting x denote σ2
v or σ2
q, we note that the partial derivatives are
positive, ∂η
∂x > 0 (i.e., keeping I constant). To derive the equilibrium eﬀects of a change in
risk, we rewrite (14) and (15) abstractly as
0 = −1
2η + γc(M, A) ≡gI(I, M) = gI(I(M), M)
(A38)
0 = −1
2η + γkM
A ≡gM(I, M) = gM(I, M(I)),
(A39)
and note that I being maximal implies that the diﬀerence I−1(I) −M(I) increases in a
neighborhood of the equilibrium I, or M′(I) < (I−1)′(I).
Using subscripts to indicate
50


<!-- PAGE 54 -->

partial derivatives, this translates into23
−gM
I
gM
M
< −gI
I
gI
M
,
(A40)
which is equivalent to
gI
MgM
I < gI
IgM
M
(A41)
because gI
M < 0 and gM
M > 0. The dependence of I and M on x is given as a solution to
gM
I
gM
M
gI
A
gA
M
  Ix
Mx

=
1
2
∂η
∂x
 1
1

,
(A42)
and therefore by
 Ix
Mx

=
1
gI
MgM
I −gI
IgM
M
gI
M −gM
M
gM
I −gI
I
 1
2
∂η
∂x

.
(A43)
We note that gI
M −gM
M < 0 and gM
I −gI
I < 0, while the determinant gI
MgM
I −gI
IgM
M is
negative from (A41). Thus, both I and M increase as σ2
v or σ2
q increases.
By dividing equation (14) by (15), A is seen to increase with M.
The above argument covers the case in which the largest equilibrium is an interior equilib-
rium. Suppose now that M = ¯
M in equilibrium, and gM(I, ¯
M) < 0. Then, the equilibrium
is determined by (A38) and M = ¯
M, and the sign of Ix is given by that of gM
I , which is
positive.
Alternatively, consider the case in which I = ¯A + M N
¯
M in the largest equilibrium. Here,
gI(I, ¯
M) < 0, and locally I = ¯A + M N
¯
M , or A = ¯A. The equilibrium is determined by (A39)
and this condition. It is immediate that M increases with x, and therefore so does I.
The eﬀect on the eﬃciency of the asset market, however, is in general not determined.
To see this clearly, diﬀerentiate (14) to get
1
2
dη
dx = γ (cMMx + cAAx) ,
(A44)
and recall that cM ≤0 and cA ≥0. Since Mx > 0 and Ax > 0, by setting one of the partial
derivatives cM and cA to zero and keeping the other nonzero, the sign of dη
dx can be made
either positive or negative. Consequently, the eﬃciency may increase as well as decrease, a
conclusion that translates to the fee f.
Exactly the same argument works when increasing (σv, σε) or (σv, σε, σq) proportionally.
Proof of Proposition 5: This proposition follows from the discussion in Appendix A.3.
23Note that gI(I(M), M) can be written as gI(I, I−1(I)) for I = I(M).
51


<!-- PAGE 55 -->

Proof of Proposition 6:
The manager’s utility decreases strictly with k.
Proof of Proposition 7:
We compute the expected return on the wealth invested with
a manager, working under the assumptions that all managers choose positions targeting
investors with relative risk aversion ¯γR. Given the total wealth under management ¯W, the
manager invests as an agent with absolute risk aversion ¯γ = ¯γR/ ¯W. It is clear that all
investors with an informed manager achieve the same gross excess return. The expected
gross return is computed as the total dollar proﬁt per capital invested ¯W, using the fact that
the aggregate position is (¯γVar (v|s))−1 (E[v|s] −p), that is,
¯Ri ≡E
 1
¯W (¯γVar (v|s))−1 (E[v|s] −p) (v −p)

= 1
¯γRE

SR2
i

.
(A45)
Similarly, the expected gross return to an investor with an uninformed manager is
¯Ru ≡E
 1
¯W (¯γVar (v|p))−1 (E[v|p] −p) (v −p)

= 1
¯γRE

SR2
u

.
(A46)
There are two reasons why E [SR2
i ] > E [SR2
u]: better information, and lower risk (which
translates into higher leverage, in absolute value). The second eﬀect is not necessary for the
result. As for the ﬁrst eﬀect, namely the fact that
E

(E[v −p|s, p])2
> E

(E[v −p|p])2
,
(A47)
it follows immediately from Jensen’s inequality (conditional on p).
Consider now the expected return of an investor in a fund conditional on the investor’s
characteristics:
E[R|Wa, γR
a , ca] = Pr(i|Wa, γR
a , ca) ¯Ri + (1 −Pr(i|Wa, γR
a , ca)) ¯Ru ,
(A48)
where Pr(i|Wa, γR
a , ca) = 1(2γR
a ca<ηWa)
¯
A+ M
¯
M N
¯
A+N
increases with Wa. Since ¯Ri > ¯Ru, it follows
that E[R|Wa, γR
a , ca] increases with Wa.
Percentage fees for a given investor are a ﬁxed multiple of
γR
a ca
Wa , a term that clearly
decreases with Wa. Consequently, the conclusion holds for after-fee returns as well.
Precisely the same argument applies to the level of sophistication (ca), albeit with re-
versed signs.
Proof of Proposition 8:
Let R(m) denote the return of manager m and ¯W (m) the aver-
age wealth across his investors. These two quantities are independent conditional on the
manager’s type (informed or uninformed). Since there are two manager types, t = i and
t = u, the covariance Cov(R(m), W (m)) is positive if and only if the conditional expectations
E[R(m)|t] and E[ ¯W (m)|t] are ranked the same as a function of the type t of manager.
52


<!-- PAGE 56 -->

In the present case, it is easy to see that the average investor of an informed manager
has higher wealth. Speciﬁcally,
E[Wa | t = i] =
A
A + M
¯
M N E

Wa
 γR
a ca
Wa
< η
2

+
M
¯
M N
A + M
¯
M N E [Wa] > E [Wa] ,
(A49)
since E
h
Wa
 γR
a ca
Wa < η
2
i
> E[Wa]. We already saw that ¯Ri > ¯Ru.
The conclusion also extends to after-fee returns, since the average percentage fees that
an informed manager receives from searching investors is smaller than those paid by noise
allocators:
E
γR
a ca
Wa
 γR
a ca
Wa
< η
2

< E
γR
n cn
Wn

.
(A50)
The same argument applies to any decreasing function of ca, and thus sophistication.
Part (ii) follows along the same lines, noting that the average size of an informed man-
ager’s AUM is higher than that of an uninformed manager. The statement about manager
cost k is immediate.
B.
Real-World Search and Due Diligence of Asset
Managers
Here we brieﬂy summarize some of the main real-world issues related to ﬁnding and
vetting an asset manager. While the search process involves a lot of details, the main point
that we model theoretically is that the process is time consuming and costly. For instance,
there exist more mutual funds than stocks in the U.S. Many of these mutual funds might be
charging high fees while investing with little or no real information, just like the uninformed
funds in our model (e.g., high-fee index funds, or so-called “closet indexers” that claim to
be active but in fact track the benchmark, or funds investing more in marketing than their
investment process). Therefore, ﬁnding a suitable mutual fund is not easy for investors (just
like ﬁnding a cheap stock is not easy for asset managers).
We ﬁrst consider the search and due diligence process of institutional investors such as
pension funds, insurance companies, endowments, foundations, funds of funds, family oﬃces,
and banks. Such institutional investors invite certain speciﬁc asset managers to visit their
oﬃces as well as travel to meet asset managers at their premises. If the institutional investor
is suﬃciently interested in investing with the manager, the investor often asks the manager
to ﬁll out a so-called due diligence questionnaire (DDQ), which provides a starting point
for the due diligence process. Here we provide an overview of the process to illustrate the
signiﬁcant time and cost related to the search process of ﬁnding an asset manager and doing
53


<!-- PAGE 57 -->

due diligence, but a detailed description of these items is beyond the scope of the paper.24
• Finding the Asset Manager: The Initial Meeting.
– Search. Institutional investors often have employees in charge of external man-
agers. These employees search for asset managers and often build up knowledge
of a large network of asset managers whom they can contact. Similarly, asset
managers employ business development staﬀwho maintain relationships with in-
vestors they know and try to connect with other asset owners, although hedge
funds are subject to nonsolicitation regulation preventing them from randomly
contacting potential investors and advertising. This two-way search process in-
volves a signiﬁcant amount of phone calls, emails, and repeated personal meetings,
often starting with meetings between the staﬀmembers dedicated to this search
process and later with meetings between the asset manager’s high-level portfolio
managers and the asset owner’s chief investment oﬃcer and board.
– Request for Proposal. Another way for an institutional investor to ﬁnd an asset
manager is to issue a request for proposal (RFP), which is a document that
invites asset managers to “bid” for an asset management mandate. The RFP
may describe the mandate in question (e.g., $100 million of long-only U.S. large-
cap equities) and all the information about the asset manager that is required.
– Capital Introduction. Investment banks sometimes have capital introduction (“cap
intro”) teams as part of their prime brokerage. A cap intro team introduces insti-
tutional investors to asset managers (e.g., hedge funds) that use the bank’s prime
brokerage.
– Consultants, Investment Advisors, and Placement Agents. Institutional investors
often use consultants and investment advisors to ﬁnd and vet investment managers
that meet their needs. On the ﬂip side, asset managers (e.g., private equity funds)
sometimes use placement agents to ﬁnd investors.
– Databases. Institutional investors also get ideas regarding which asset managers to
meet by looking at databases that may contain performance numbers and overall
characteristics of the covered asset managers.
• Evaluating the Asset Management Firm.
24Standard
DDQs
are
available
online,
from
example,
from
the
Managed
Funds
Association
(http://www.managedfunds.org/wp-content/uploads/2011/06/Due-Dilligence-
Questionnaire.pdf)
or
the
Institutional
Limited
Partner
Association
(http://ilpa.org/wp-
content/publicmedia/ILPA Due Diligence Questionnaire Tool.docx). See also “Best Practices in Alternative
Investments: Due Diligence,” Greenwich Roundtable, 2010 (www.greenwichroundtable.org/system/ﬁles/BP-
2010.pdf), the CFA Institute’s “Model RFP: A standardized process for selecting money managers”
(http://www.cfainstitute.org/ethics/topics/Pages/model rfp.aspx), and “Best Practices for the Hedge Fund
Industry,” Report of the Asset Managers’ Committee to the President’s working group on ﬁnancial markets,
2009 (http://www.cftc.gov/ucm/groups/public/swaps/documents/ﬁle/bestpractices.pdf). We are grateful
for helpful discussions with Stephen Mellas and Jim Riccobono at AQR Capital Management.
54


<!-- PAGE 58 -->

– Assets, Funds, and Investors. An asset manager’s overall assets under manage-
ment, the distribution of assets across fund types, client types, and location.
– People. Key personnel, overall headcount information, headcount by major de-
partments, and stability of senior people.
– Client Servicing. Services and information disclosed to investors, ongoing perfor-
mance attribution, market updates, etc.
– History, Culture, and Ownership. Year the asset management ﬁrm was founded,
how it has evolved, general investment culture, ownership of the asset management
ﬁrm, and whether the portfolio managers invest in their own funds.
• Evaluating the Speciﬁc Fund.
– Terms.
Fund structure (e.g., master-feeder), investment minimum, fees, high
water marks, hurdle rate, other fees (e.g., operating expenses, audit fees, ad-
ministrative fees, fund organizational expenses, legal fees, sales fees, salaries),
transparency of positions, and exposures.
– Redemption Terms. Any fees payable, lock-ups, gating provisions, whether the
investment manager can suspend redemptions or pay redemption proceeds in-
kind, and other restrictions.
– Asset and Investors.
Net asset value, number of investors, and whether any
investors in the fund experience fee or redemption terms that diﬀer materially
from the standard ones.
• Evaluating the Investment Process.
– Track Record. Past performance numbers and possible performance attribution.
– Instruments. Securities traded and geographical regions.
– Team. Investment personnel, experience, education, and turnover.
– Investment Thesis and Economic Reasoning. The underlying source of proﬁt, why
should the investment strategy be expected to be proﬁtable, who takes the other
side of the trade and why, and has the strategy worked historically?
– Investment Process. Analyzing the investment process and thesis is one of the
most important parts of ﬁnding an asset manager. What drives the asset man-
ager’s decisions to buy and sell, what is the investment process, what data are
used, how is information gathered and analyzed, what systems are used, etc.
– Portfolio Characteristics. Leverage, turnover, liquidity, typical number of posi-
tions, and position limits.
– Examples of Past Trades. What motivated these trades, how do they reﬂect the
general investment process, and how were positions adjusted as events evolved.
55


<!-- PAGE 59 -->

– Portfolio Construction Methodology. How is the portfolio constructed, how are
positions adjusted over time, how is risk measured, what are the position limits,
etc.
– Trading Methodology.
Connections to broker/dealers, staﬃng of trading desk,
whether trading desk operates 24/7, co-location on major exchanges, use of inter-
nal or external broker algorithms, etc.
– Financing of Trades. Prime broker relations and leverage.
• Evaluating Risk Management.
– Risk Management Team. Team members, independence, and authority.
– Risk Measures. Risk measures calculated, risk reports to investors, and stress
tests.
– Risk Management. How is risk managed, what actions are taken when risk limits
are breached, and who makes the decision.
• Due Diligence of Operational Issues and Back Oﬃce.
– Operations Overview. Teams, functions, and segregation of duties.
– Lifecycle of a Trade. What steps does a trade makes as it ﬂows through the asset
manager’s systems.
– Cash Management.
Who can move cash, how, and what controls are placed
around this process.
– Valuation. What independent pricing sources are used, what level of PM input
is there, what controls and policies ensure accurate pricing, who monitors this
internally and externally.
– Reconciliation. How frequently and granularly are cash and positions reconciled.
– Client Service. Reporting frequency, transparency levels, and other client services
and reporting.
– Service Providers. The main service providers used and any major changes (recent
or planned).
– Systems. What are the major homegrown or vendor systems with possible live
system demos.
– Counterparties. Who are the main counterparties, how are they selected, and how
and by whom is counterparty risk managed.
– Asset Veriﬁcation. Some large investors (and/or their consultants) will ask to
speak directly to the asset manager’s administrator to independently verify that
assets are valued correctly.
56


<!-- PAGE 60 -->

• Due Diligence of Compliance, Corporate Governance, and Regulatory Issues.
– Overview. Teams, functions, and independence.
– Regulators and Regulatory Reporting. Who are the regulators for the fund, sum-
mary of recent visits/interactions, and frequency of reporting.
– Corporate Governance. Summary of policies and oversight.
– Employee Training. Code of ethics and training.
– Personal Trading. What is the policy, recent violations of the policy, and what is
the penalty for breach.
– Litigation. What litigation has the ﬁrm been involved with.
• Due Diligence of Business Continuity Plan (BCP) and Disaster Recovery Plan.
– Plan Overview. Policy, staﬃng, and backup facilities.
– Testing. Frequency and intensity of tests.
– Cybersecurity. How are IT systems and networks defended and tested.
The search process for ﬁnding an asset manager is very diﬀerent for retail investors.
Clearly, there is no standard structure for the search process for retail investors, but here
are some considerations:
• Retail Investors Searching for an Asset Manager.
– Online Search. Some retail investors search for useful information about investing
online and may make their investment online. However, ﬁnding the right websites
may require signiﬁcant search eﬀort and, once located, ﬁnding and understanding
the right information on the website can be diﬃcult as discussed further below.
– Walking into a Local Branch of a Financial Institution.
Retail investors may
prefer to invest in person, for example, by walking into the local branch of a
ﬁnancial institution such as a bank, insurance provider, or investment ﬁrm. Vis-
iting multiple ﬁnancial institutions can be time consuming and confusing for retail
investors.
– Brokers and Intermediaries. Bergstresser, Chalmers, and Tufano (2009) report
that a large fraction of mutual funds are sold via brokers and study the charac-
teristics of these fund ﬂows.
– Choosing from Pension System Menu. Lastly, retail investors get exposure to
asset management through their pension systems. In deﬁned contribution pension
schemes, retail investors must search through a menu of options for their preferred
fund.
• Searching for the Relevant Information.
57


<!-- PAGE 61 -->

– Fees. Choi, Laibson, and Madrian (2010) ﬁnd experimental evidence that “search
costs for fees matter.” In particular, their study “asked 730 experimental subjects
to allocate $10,000 among four real S&P 500 index funds. All subjects received
the funds prospectuses. To make choices incentive-compatible, subjects expected
payments depended on the actual returns of their portfolios over a speciﬁed time
period after the experimental session. ... In one treatment condition, we gave
subjects a one-page ‘cheat sheet’ that summarized the funds front-end loads and
expense ratios. ... We ﬁnd that eliminating search costs for fees improved portfolio
allocations.”
– Fund Objective and Skill. Choi, Laibson, and Madrian (2010) also ﬁnd evidence
that investors face search costs associated with the funds’ objectives such as the
meaning of an index fund. “In a second treatment condition, we distributed one
page of answers to frequently asked questions (FAQs) about S&P 500 index funds.
... When we explained what S&P 500 index funds are in the FAQ treatment,
portfolio fees dropped modestly, but the statistical signiﬁcance of this drop is
marginal.”
– Price and Net Asset Value. In some countries, retail investors buy and sell mutual
fund shares as listed shares on an exchange.
In this case, a central piece of
information is the relation between the share price and the mutual fund’s net
asset value, but investors must search for these pieces of information on diﬀerent
websites and often they are not synchronous.
• Understanding the Relevant Information.
– Financial Literacy. In their study on the choice of index funds, Choi, Laibson, and
Madrian (2010) ﬁnd that “fees paid decrease with ﬁnancial literacy.” Simply un-
derstanding the relevant information and, in particular, the (lack of) importance
of past returns is an important part of the issue.
– Opportunity Costs. Even for ﬁnancially literate investors, the nontrivial amount
of time it takes to search for a good asset manager may be viewed as a signiﬁcant
opportunity cost given that people have other productive uses of their time and
value leisure time.
58


<!-- PAGE 62 -->

REFERENCES
Admati, Anat R., 1985, A noisy rational expectations equilibrium for multi-asset securities
markets, Econometrica 53, 629–657.
Admati, Anat R., and Paul Pﬂeiderer, 1988, Selling and trading on information in ﬁnancial
markets, American Economic Review 78, 96–103.
Bai, Jennie, Thomas Philippon, and Alexi Savov, 2013, Have ﬁnancial markets become more
informative?, Working paper, National Bureau of Economic Research.
Bergstresser, Daniel, John MR Chalmers, and Peter Tufano, 2009, Assessing the costs and
beneﬁts of brokers in the mutual fund industry, Review of Financial Studies 22, 4129–4156.
Berk, Jonathan B., and Jules H. Van Binsbergen, 2015, Measuring skill in the mutual fund
industry, Journal of Financial Economics 118, 1–20.
Berk, Jonathan B., and Richard C. Green, 2004, Mutual fund ﬂows and performance in
rational markets, Journal of Political Economy 112, 1269–1295.
Buﬀa, Andrea M., Dimitri Vayanos, and Paul Woolley, 2014, Asset management contracts
and equilibrium prices, Working paper, Boston University.
Carhart, Mark M., 1997, On persistence in mutual fund performance, The Journal of Finance
52, 57–82.
Chen, Joseph, Harrison Hong, Ming Huang, and Jeﬀrey D Kubik, 2004, Does fund size erode
mutual fund performance? The role of liquidity and organization, American Economic
Review 94, 1276–1302.
Chevalier, Judith, and Glenn Ellison, 1999, Are some mutual fund managers better than
others? Cross-sectional patterns in behavior and performance, The Journal of Finance
54, 875–899.
Choi, James J, David Laibson, and Brigitte C Madrian, 2010, Why does the law of one price
fail? An experiment on index mutual funds, Review of Financial Studies 23, 1405–1432.
Cuoco, Domenico, and Ron Kaniel, 2011, Equilibrium prices in the presence of delegated
portfolio management, Journal of Financial Economics 101, 264–296.
Diamond, Douglas W., and Robert E. Verrecchia, 1981, Information aggregation in a noisy
rational expectations economy, Journal of Financial Economics 9, 221–235.
Duﬃe, Darrell, Nicolae Gˆarleanu, and Lasse Heje Pedersen, 2005, Over-the-counter markets,
Econometrica 73, 1815–1847.
Dyck, Alexander, Karl V Lins, and Lukasz Pomorski, 2013, Does active management pay?
New international evidence, The Review of Asset Pricing Studies 3, 200–228.
59


<!-- PAGE 63 -->

Dyck, IJ, and Lukasz Pomorski, 2016, Investor scale and performance in private equity
investments, Review of Finance 20, 1081–1106.
Evans, Richard B, and R¨udiger Fahlenbrach, 2012, Institutional investors and mutual fund
governance: Evidence from retail–institutional fund twins, Review of Financial Studies
25, 3530–3571.
Fama, Eugene F., 1970, Eﬃcient capital markets: A review of theory and empirical work,
Journal of Finance 25, 383–417.
Fama, Eugene F, and Kenneth R French, 2010, Luck versus skill in the cross-section of
mutual fund returns, The Journal of Finance 65, 1915–1947.
Ferreira, Miguel A, Aneel Keswani, Ant´onio F Miguel, and Soﬁa B Ramos, 2013, The de-
terminants of mutual fund performance: A cross-country study, Review of Finance 17,
483–525.
Fung, William, David A. Hsieh, Narayan Y Naik, and Tarun Ramadorai, 2008, Hedge funds:
Performance, risk, and capital formation, The Journal of Finance 63, 1777–1803.
Garc´ıa, Diego, and Joel M. Vanden, 2009, Information acquisition and mutual funds, Journal
of Economic Theory 144, 1965–1995.
Gennaioli, Nicola, Andrei Shleifer, and Robert Vishny, 2015, Money doctors, The Journal
of Finance 70, 91–114.
Gerakos, Joseph, Juhani T. Linnainmaa, and Adair Morse, 2016, Asset managers: Institu-
tional performance and smart betas, Working paper, Dartmouth College.
Glosten, Lawrence R., and Paul R. Milgrom, 1985, Bid, ask and transaction prices in a
specialist market with heterogeneously informed traders, Journal of Financial Economics
14, 71–100.
Grinblatt, Mark, and Sheridan Titman, 1989, Mutual fund performance: An analysis of
quarterly portfolio holdings, Journal of business 62, 393–416.
Grossman, Sanford J., 1976, On the eﬃciency of competitive stock markets where traders
have diverse information, Journal of Finance 31, 573–585.
Grossman, Sanford J., and Joseph E. Stiglitz, 1980, On the impossibility of informationally
eﬃcient markets, American Economic Review 70, 393–408.
Guercio, Diane Del, and Jonathan Reuter, 2014, Mutual fund performance and the incentive
to generate alpha, Journal of Finance 69, 1673–1704.
Hellwig, Martin F., 1980, On the aggregation of information in competitive markets, Journal
of Economic Theory 22, 477–498.
60


<!-- PAGE 64 -->

Horta¸csu, Ali, and Chad Syverson, 2004, Product diﬀerentiation, search costs, and competi-
tion in the mutual fund industry: A case study of the S&P 500 index funds, The Quarterly
Journal of Economics 119, 403–456.
Jagannathan, Ravi, Alexey Malakhov, and Dmitry Novikov, 2010, Do hot hands exist among
hedge fund managers? An empirical evaluation, Journal of Finance 65, 217–255.
Jain, Prem C., and Joanna Shuang Wu, 2000, Truth in mutual fund advertising: Evidence
on future performance and fund ﬂows, The Journal of Finance 55, 937–958.
Kacperczyk, Marcin, Stijn Van Nieuwerburgh, and Laura Veldkamp, 2014, Time-varying
fund manager skill, Journal of Finance 69, 1455–1484.
Kacperczyk, Marcin, Clemens Sialm, and Lu Zheng, 2008, Unobserved actions of mutual
funds, Review of Financial Studies 21, 2379–2416.
Kacperczyk, Marcin, Stijn Van Nieuwerburgh, and Laura Veldkamp, 2016, A rational theory
of mutual funds’ attention allocation, Econometrica 84, 571–626.
Kaplan, Steven N, and Antoinette Schoar, 2005, Private equity performance: Returns, per-
sistence, and capital ﬂows, Journal of Finance 60, 1791–1823.
Keswani, Aneel, Miguel A Ferreira, Antonio F Miguel, and Soﬁa Brito Ramos, 2016, Testing
the Berk and Green model around the world, Working paper, Cass Business School.
Khorana, Ajay, Henri Servaes, and Peter Tufano, 2008, Mutual fund fees around the world,
Review of Financial Studies 22, 1279–1310.
Korteweg, Arthur G., and Morten Sorensen, 2017, Skill and luck in private equity perfor-
mance, Journal of Financial Economics 124, 535–562.
Kosowski, Robert, Narayan Y Naik, and Melvyn Teo, 2007, Do hedge funds deliver alpha?
A Bayesian and bootstrap analysis, Journal of Financial Economics 84, 229–264.
Kosowski, Robert, Allan Timmermann, Russ Wermers, and Hal White, 2006, Can mutual
fund stars really pick stocks? New evidence from a bootstrap analysis, Journal of Finance
61, 2551–2595.
Kyle, Albert S., 1985, Continuous auctions and insider trading, Econometrica 6, 1315–1335.
Lagos, Ricardo, 2010, Asset prices and liquidity in an exchange economy, Journal of Mone-
tary Economics 57, 913–930.
Palvolgyi, Domotor, and Gyuri Venter, 2014, Multiple equilibria in noisy rational expecta-
tions economies, Working paper, Eotvos Lorand University.
Pastor, Lubos, and Robert F. Stambaugh, 2012, On the size of the active management
industry, Journal of Political Economy 120, 740–781.
61


<!-- PAGE 65 -->

Pastor, Lubos, Robert F. Stambaugh, and Lucian A Taylor, 2015, Scale and skill in active
management, Journal of Financial Economics 116, 23–45.
Pedersen, Lasse Heje, 2015, Eﬃciently Ineﬃcient: How Smart Money Invests and Market
Prices Are Determined. (Princeton University Press, Princeton, NJ).
Rosch, Dominik M., Avanidhar Subrahmanyam, and Mathijs A. van Dijk, 2015, An empirical
analysis of co-movement in market eﬃciency measures, Working paper, Rotterdam School
of Management.
Ross, Stephen A., 2005, Markets for agents: Fund management, in Bruce N. Lehmann, eds.:
The Legacy of Fischer Black (Oxford University Press, New York, NY ).
Shleifer, Andrei, and Robert W. Vishny, 1997, Limits of arbitrage, Journal of Finance 52,
35–55.
Sialm, Clemens, Zheng Sun, and Lu Zheng, 2014, Home bias and local contagion: Evidence
from funds of hedge funds, Working paper, University of Texas at Austin.
Sirri, Erik R., and Peter Tufano, 1998, Costly search and mutual fund ﬂows, The Journal of
Finance 53, 1589–1622.
Stambaugh, Robert F., 2014, Presidential address: Investment noise and trends, Journal of
Finance 69, 1415–1453.
Stein, Jeremy C., 2005, Why are most funds open-end?
Competition and the limits of
arbitrage, Quarterly Journal of Economics 120, 247–272.
Van Nieuwerburgh, Stijn, and Laura Veldkamp, 2010, Information acquisition and under-
diversiﬁcation, Review of Economic Studies 77, 779–805.
Vayanos, Dimitri, and Paul Woolley, 2013, An institutional theory of momentum and rever-
sal, Review of Financial Studies 26, 1087–1145.
Verrecchia, Robert E, 1982, Information acquisition in a noisy rational expectations economy,
Econometrica 50, 1415–1430.
Wermers, Russ, 2000, Mutual fund performance: An empirical decomposition into stock-
picking talent, style, transactions costs, and expenses, Journal of Finance 55, 1655–1703.
Wurgler, Jeﬀrey, 2000, Financial markets and the allocation of capital, Journal of Financial
Economics 58, 187–214.
62
