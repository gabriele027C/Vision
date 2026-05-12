---
source_file: "de Prado, Ph.D..pdf"
total_pages: 28
---



<!-- PAGE 1 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
 
Marcos López de Prado, Ph.D. 
Advances in Financial Machine Learning 
ORIE 5256 
Backtesting II


<!-- PAGE 2 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
What are we going to learn today? 
• Backtest Statistics 
oGeneral Characteristics 
oPerformance 
oTime-Weighted Rate of Return 
oDrawdown and Time Under Water 
oImplementation Shortfall 
oEfficiency 
oClassification Scores 
• Understanding Strategy Risk 
oSymmetric Payouts 
oAsymmetric Payouts 
oThe Probability of Strategy Failure 
2


<!-- PAGE 3 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
Backtest Statistics


<!-- PAGE 4 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
General Statistics 
• Time range: Time range specifies the start and end dates. 
• Average AUM: This is the average dollar value of the assets under management. 
• Capacity: A strategy’s capacity can be measured as the highest AUM that delivers a target risk-
adjusted performance. 
• Leverage: Leverage measures the amount of borrowing needed to achieve the reported 
performance. 
• Maximum dollar position size: Maximum dollar position size informs us whether the strategy at 
times took dollar positions that greatly exceeded the average AUM. 
• Ratio of longs: The ratio of longs show what proportion of the bets involved long positions. 
• Frequency of bets: The frequency of bets is the number of bets per year in the backtest. 
• Average holding period: The average holding period is the average number of days a bet is held. 
• Annualized turnover: Annualized turnover measures the ratio of the average dollar amount 
traded per year to the average annual AUM. 
• Correlation to underlying: This is the correlation between strategy returns and the returns of the 
underlying investment universe. 
4


<!-- PAGE 5 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
Performance 
• PnL: The total amount of dollars (or the equivalent in the currency of 
denomination) generated over the entirety of the backtest, including 
liquidation costs from the terminal position. 
• PnL from long positions: The portion of the PnL dollars that was generated 
exclusively by long positions. 
• Annualized rate of return: The time-weighted average annual rate of total 
return, including dividends, coupons, costs, etc. 
• Hit ratio: The fraction of bets that resulted in a positive PnL. 
• Average return from hits: The average return from bets that generated a 
profit. 
• Average return from misses: The average return from bets that generated 
a loss. 
5


<!-- PAGE 6 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
Time-Weighted Rate of Return (1/2) 
• The TWRR for portfolio i between subperiods 𝑡−1, 𝑡 is denoted 𝑟𝑖,𝑡, with equations 
𝑟𝑖,𝑡= 𝜋𝑖,𝑡
𝐾𝑖,𝑡
; 𝜋𝑖,𝑡=  
∆𝑃𝑗,𝑡+ 𝐴𝑗,𝑡𝜃𝑖,𝑗,𝑡−1 + ∆𝜃𝑖,𝑗,𝑡𝑃𝑗,𝑡−𝑃 𝑗,𝑡−1
𝐽
𝑗=1
 
𝐾𝑖,𝑡=  𝑃 𝑗,𝑡−1𝜃𝑖,𝑗,𝑡−1
𝐽
𝑗=1
+ max 0,  𝑃  
𝑗,𝑡∆𝜃𝑖,𝑗,𝑡
𝐽
𝑗=1
 
where 
o 𝜋𝑖,𝑡 is the mark-to-market (MtM) profit or loss for portfolio i at time t. 
o 𝐾𝑖,𝑡 is the market value of the assets under management by portfolio i through subperiod t. The purpose of 
including the max .  term is to fund additional purchases (ramp-up). 
o 𝐴𝑗,𝑡 is the interest accrued or dividend paid by one unit of instrument j at time t. 
o 𝑃𝑗,𝑡 is the clean price of security j at time t. 
o 𝜃𝑖,𝑗,𝑡 are the holdings of portfolio i on security j at time t. 
6


<!-- PAGE 7 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
Time-Weighted Rate of Return (2/2) 
… where (continued) 
o 𝑃 𝑗,𝑡 is the dirty price of security j at time t. 
o 𝑃 𝑗,𝑡 is the average transacted clean price of portfolio i on security j over subperiod t. 
o 𝑃  
𝑗,𝑡 is the average transacted dirty price of portfolio i on security j over subperiod t. 
• Inflows are assumed to occur at the beginning of the day, and outflows are assumed to occur at the end of the day. These 
sub-period returns are then linked geometrically as 
𝜑𝑖,𝑇=  (1 + 𝑟𝑖,𝑡)
𝑇
𝑡=1
 
• The variable 𝜑𝑖,𝑇 can be understood as the performance of one dollar invested in portfolio i over its entire life, 𝑡= 1, . . . , 𝑇. 
Finally, the annualized rate of return of portfolio i is 
𝑅𝑖= 𝜑𝑖,𝑇
−𝑦𝑖−1 
where 𝑦𝑖 is the number of years elapsed between 𝑟𝑖,1 and 𝑟𝑖,𝑇. 
7


<!-- PAGE 8 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
Drawdown and Time Under Water 
• Intuitively, a drawdown (DD) is the maximum loss suffered by an 
investment between two consecutive high-watermarks (HWMs). 
• The time under water (TuW) is the time elapsed between an HWM 
and the moment the PnL exceeds the previous maximum PnL. 
8 
def computeDD_TuW(series,dollars=False): 
    # compute series of drawdowns and the time under water associated with them 
    df0=series.to_frame('pnl') 
    df0['hwm']=series.expanding().max() 
    df1=df0.groupby('hwm').min().reset_index() 
    df1.columns=['hwm','min'] 
    df1.index=df0['hwm'].drop_duplicates(keep='first').index  # time of hwm 
    df1=df1[df1['hwm']>df1['min']] # hwm followed by a drawdown 
    if dollars:dd=df1['hwm']-df1['min'] 
    else:dd=1-df1['min']/df1['hwm'] 
    tuw=((df1.index[1:]-df1.index[:-1])/np.timedelta64(1,'Y')).values # in years 
    tuw=pd.Series(tuw,index=df1.index[:-1]) 
    return dd,tuw


<!-- PAGE 9 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
Implementation Shortfall 
• Broker fees per turnover: These are the fees paid to the broker for 
turning the portfolio over, including exchange fees. 
• Average slippage per turnover: These are execution costs, excluding 
broker fees, involved in one portfolio turnover. 
• Dollar performance per turnover: This is the ratio between dollar 
performance (including brokerage fees and slippage costs) and total 
portfolio turnovers. 
• Return on execution costs: This is the ratio between dollar 
performance (including brokerage fees and slippage costs) and total 
execution costs. 
9


<!-- PAGE 10 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
Efficiency 
• Annualized Sharpe ratio: This is the SR value, annualized by a factor 
𝑎, where 𝑎 is the average number of returns observed per year. 
• Information ratio: This is the SR equivalent of a portfolio that 
measures its performance relative to a benchmark. 
• Probabilistic Sharpe ratio: PSR corrects SR for inflationary effects 
caused by non-Normal returns or track record length. 
• Deflated Sharpe ratio: DSR corrects SR for inflationary effects caused 
by non-Normal returns, track record length, and selection bias under 
multiple testing. 
10


<!-- PAGE 11 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
Sharpe [1966] 
11 
• Consider an investment strategy with excess returns (or risk premia) 𝑟𝑡, 𝑡= 1, … , 𝑇, which follow an IID 
Normal distribution, 
 
𝑟𝑡~𝒩𝜇, 𝜎2  
  
where 𝒩𝜇, 𝜎2  represents a Normal distribution with mean 𝜇 and variance 𝜎2.  
• The SR (non-annualized) of such strategy is defined as 
  
𝑆𝑅= 𝜇
𝜎 
  
• Because parameters 𝜇 and 𝜎 are not known, SR is estimated as 
 
𝑆𝑅
 = E 𝑟𝑡
V 𝑟𝑡


<!-- PAGE 12 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
Lo [2002] 
12 
• Under the assumption that returns follow an IID Normal distribution, Lo [2002] derived the asymptotic 
distribution of 𝑆𝑅
  as 
 
𝑆𝑅
 −𝑆𝑅
𝑎 𝒩0,
1 + 1
2 𝑆𝑅2
𝑇
 
  
• Under the assumption that returns follow an IID non-Normal distribution, Mertens [2002] derived the 
asymptotic distribution of 𝑆𝑅
  as 
  
𝑆𝑅
 −𝑆𝑅
𝑎 𝒩0,
1 + 1
2 𝑆𝑅2 −𝛾3𝑆𝑅+ 𝛾4 −3
4
𝑆𝑅2
𝑇
 
  
where 𝛾3 is the skewness of 𝑟𝑡, and 𝛾4 is the kurtosis of 𝑟𝑡 (𝛾3 = 0 and 𝛾4 = 3 when returns follow a Normal 
distribution).


<!-- PAGE 13 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
Bailey and López de Prado [2012] (1/2) 
13 
• Christie [2005] and Opdyke [2007] discovered that, in fact, the Mertens [2002] equation is also valid under the 
more general assumption that returns are stationary and ergodic (not necessarily IID). 
• Bailey and López de Prado [2012] utilized those results to derive the Probabilistic Sharpe Ratio (PSR). 
• PSR estimates the probability that an observed 𝑆𝑅
  exceeds 𝑆𝑅∗ as 
 
𝑃𝑆𝑅
 
𝑆𝑅∗= 𝑍
𝑆𝑅
 −𝑆𝑅∗
𝑇−1
1 −𝛾 3𝑆𝑅
 + 𝛾 4 −1
4
𝑆𝑅
 2
 
  
where 𝑍.  is the CDF of the standard Normal distribution, T is the number of  observed returns, 𝛾 3 is the 
skewness of the returns, and 𝛾 4 is the kurtosis of the returns. Note that 𝑆𝑅
  is the non-annualized estimate of SR, 
computed on the same frequency as the T observations.


<!-- PAGE 14 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
Bailey and López de Prado [2012] (2/2) 
14 
• For a given 𝑆𝑅∗, 𝑃𝑆𝑅
  increases with  
• greater mean returns (E 𝑟𝑡) 
• lower variance of returns (V 𝑟𝑡) 
• longer track records (T) 
• positively skewed returns (𝛾 3) 
• thinner tails (𝛾 4) 
• This result also allows us to answer the question: “How long should a track record be in order to have statistical 
confidence 1 −𝛼 that its estimated Sharpe ratio (𝑆𝑅
 ) is above a given threshold (𝑆𝑅∗)” (minimum track record 
length) 
 
𝑀𝑖𝑛𝑇𝑅𝐿= 1 + 1 −𝛾 3𝑆𝑅
 + 𝛾 4 −1
4
𝑆𝑅
 2
𝑍𝛼
𝑆𝑅
 −𝑆𝑅∗
2
 
 
where 𝑍𝛼 is the value of the Standard Normal CDF that leaves a probability 𝛼 in the right tail.


<!-- PAGE 15 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
Bailey and López de Prado [2014] (1/2) 
15 
• The Deflated Sharpe Ratio computes the probability that the Sharpe Ratio (SR) is statistically significant, after 
controlling for the inflationary effect of multiple trials, data dredging, non-normal returns and shorter sample 
lengths. 
 
𝐷𝑆𝑅
 ≡𝑃𝑆𝑅
 
𝑆𝑅
 0 = 𝑍
𝑆𝑅
 −𝑆𝑅
 0
𝑇−1
1 −𝛾 3𝑆𝑅
 + 𝛾 4 −1
4
𝑆𝑅
 2
 
 
 
where 𝑆𝑅
 0 is the estimate provided by the False Strategy theorem, 
 
𝑆𝑅
 0 =
V 𝑆𝑅
 𝑘
1 −𝛾𝑍−1 1 −1
𝐾+ 𝛾𝑍−1 1 −1
𝐾𝑒
 
 
• DSR packs more information than SR, and it is expressed in probabilistic terms.


<!-- PAGE 16 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
Bailey and López de Prado [2014] (2/2) 
16 
• The standard SR is computed as a function of two estimates: 
• Mean of returns 
• Standard deviation of returns 
• DSR deflates SR by taking into consideration five additional variables (it packs more information): 
• The non-Normality of the returns 𝛾 3, 𝛾 4  
• The length of the returns series 𝑇 
• The amount of data dredging V 𝑆𝑅
 𝑘
 
• The number of independent trials involved in the selection of the investment strategy 𝐾 
The key to preventing selection bias is to record all trials, and determine correctly the number of 
effectively independent trials (K).


<!-- PAGE 17 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
Classification Scores 
• Accuracy: The fraction of opportunities correctly labeled. 
• Precision: The fraction of true positives among the predicted positives. 
• Recall: The fraction of true positives among the positives. 
• F1: The (equally weighted) harmonic mean of precision and recall. 
• Log-loss (cross-entropy loss): It computes the log-likelihood of the classifier given the true label, which takes 
predictions’ probabilities into account. Log loss can be estimated as follows: 
𝐿𝑌, 𝑃= −log Prob 𝑌 𝑃
= −𝑁−1   𝑦𝑛,𝑘log 𝑝𝑛,𝑘
𝐾−1
𝑘=0
𝑁−1
𝑛=0
 
where: 
o 𝑝𝑛,𝑘 is the probability associated with prediction n of label k. 
o 𝑌 is a 1-of-K binary indicator matrix, such that 𝑦𝑛,𝑘= 1 when observation 𝑛 was assigned label 𝑘 out of K 
possible labels, and 0 otherwise. 
 
 
17


<!-- PAGE 18 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
Understanding Strategy Risk


<!-- PAGE 19 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
Symmetric Payouts (1/2) 
• Consider a strategy that produces n IID bets per year, where the outcome 𝑋𝑖 of a bet 𝑖∈1, 𝑛 is a profit 
𝜋> 0 with probability P 𝑋𝑖= 𝜋= 𝑝, and a loss – 𝜋 with probability P 𝑋𝑖= −𝜋= 1 −𝑝.  
• Think of 𝑝 as the precision of a binary classifier where a positive means betting on an opportunity, and a 
negative means passing on an opportunity: True positives are rewarded, false positives are punished, and 
negatives (whether true or false) have no payout.  
• Since the betting outcomes 𝑋𝑖𝑖=1,...,𝑛 are independent, we compute the expected moments per bet: 
o The expected profit from one bet is E 𝑋𝑖= 𝜋𝑝+ −𝜋
1 −𝑝= 𝜋2𝑝−1 . 
o The variance is V 𝑋𝑖= E 𝑋𝑖
2 −E 𝑋𝑖2, where E 𝑋𝑖
2 = 𝜋2𝑝+ −𝜋2 1 −𝑝= 𝜋2, thus V 𝑋𝑖= 𝜋2 −𝜋2 2𝑝−1 2 =
𝜋2 1 −2𝑝−1 2 = 4𝜋2𝑝1 −𝑝. 
• For n IID bets per year, the annualized Sharpe ratio (𝜃) is 
𝜃𝑝, 𝑛= 𝑛E 𝑋𝑖
𝑛V 𝑋𝑖
=
2𝑝−1
2 𝑝1 −𝑝
t−value of 𝑝
under H0:𝑝=1
2
𝑛 
19


<!-- PAGE 20 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
Symmetric Payouts (2/2) 
• Note how 𝜋 cancels out of the above equation, because the payouts are symmetric. 
• Just as in the Gaussian case, 𝜃𝑝, 𝑛 can be understood as a re-scaled t-value. 
• This illustrates the point that, even for a small 𝑝>
1
2, the Sharpe ratio can be made high 
for a sufficiently large n. 
• This is the economic basis for high-frequency trading, where 𝒑 can be barely above .5, 
and the key to a successful business is to increase 𝒏.  
• The Sharpe ratio is a function of precision rather than accuracy, because passing on an 
opportunity (a negative) is not rewarded or punished directly (although too many 
negatives may lead to a small n, which will depress the Sharpe ratio toward zero). 
o For example, 𝑝= .55 ⟹
2𝑝−1
2 𝑝1−𝑝= 0.1005, and achieving an annualized Sharpe ratio of 2 
requires 396 bets per year. 
20


<!-- PAGE 21 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
Asymmetric Payouts 
• Consider a strategy that produces n IID bets per year, where the outcome 𝑋𝑖 of a bet 
𝑖∈1, 𝑛 is 𝜋+ with probability P 𝑋𝑖= 𝜋+ = 𝑝, and an outcome 𝜋−, 𝜋−< 𝜋+ occurs 
with probability P 𝑋𝑖= 𝜋−= 1 −𝑝.  
o The expected profit from one bet is E 𝑋𝑖= 𝑝𝜋+ + 1 −𝑝𝜋−= 𝜋+ −𝜋−𝑝+ 𝜋−.  
o The variance is V 𝑋𝑖= E 𝑋𝑖
2 −E 𝑋𝑖2, where E 𝑋𝑖
2 = 𝑝𝜋+
2 + 1 −𝑝𝜋−2 = 𝜋+
2 −𝜋−2 𝑝+ 𝜋−2 , 
thus V 𝑋𝑖= 𝜋+ −𝜋−2𝑝1 −𝑝.  
• For n IID bets per year, the annualized Sharpe ratio (𝜃) is 
𝜃𝑝, 𝑛, 𝜋−, 𝜋+ = 𝑛E 𝑋𝑖
𝑛V 𝑋𝑖
=
𝜋+ −𝜋−𝑝+ 𝜋−
𝜋+ −𝜋−
𝑝1 −𝑝
𝑛 
and for 𝜋−= −𝜋+ we can see that this equation reduces to the symmetric case: 
𝜃𝑝, 𝑛, −𝜋+, 𝜋+ =
2𝜋+𝑝+𝜋+
2𝜋+ 𝑝1−𝑝
𝑛=
2𝑝−1
2 𝑝1−𝑝
𝑛= 𝜃𝑝, 𝑛. 
• For example, for 𝑛= 260, 𝜋−= −.01, 𝜋+ = .005, 𝑝= .7, we get 𝜃= 1.173. 
 
21


<!-- PAGE 22 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
The Probability of Strategy Failure (1/2) 
• In the example above, parameters  
o 𝜋−= −.01, 𝜋+ = .005 are set by the portfolio manager, and passed to the traders with the execution orders. 
o Parameter 𝑛= 260 is also set by the portfolio manager, as she decides what constitutes an opportunity worth betting on. 
• The two parameters that are not under the control of the portfolio manager are 𝑝 (determined by the 
market) and 𝜃∗ (the objective set by the investor). Because 𝑝 is unknown, we can model it as a random 
variable, with expected value E 𝑝.  
• Let us define 𝑝𝜃∗ as the value of p below which the strategy will underperform a target Sharpe ratio 𝜃∗, that 
is, 𝑝𝜃∗= max 𝑝 𝜃≤𝜃∗.  
• For 𝑝𝜃∗=0 =
2
3, 𝑝< 𝑝𝜃∗=0 ⟹𝜃≤0. This highlights the risks involved in this strategy, because a relatively 
small drop in p (from 𝑝= .7 to 𝑝= .67) will wipe out all the profits. The strategy is intrinsically risky, even if 
the holdings are not. 
• That is a critical difference missing in most asset management textbooks: Strategy risk should not be 
confused with portfolio risk. 
22


<!-- PAGE 23 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
The Probability of Strategy Failure (2/2) 
• Firms and investors compute, monitor, and report portfolio risk 
without realizing that this tells us nothing about the risk of the 
strategy itself.  
• Strategy risk is not the risk of the underlying portfolio, as computed 
by the chief risk officer.  
• Strategy risk is the risk that the strategy will fail to succeed over time, 
a question of far greater relevance to the chief investment officer. 
• The answer to the question “What is the probability that this strategy 
will fail?” is equivalent to computing P 𝑝< 𝑝𝜃∗. 
23


<!-- PAGE 24 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
For Additional Details 
24 
The first wave of quantitative innovation in finance was led by Markowitz 
optimization. Machine Learning is the second wave and it will touch every 
aspect of finance. López de Prado’s Advances in Financial Machine Learning 
is essential for readers who want to be ahead of the technology rather than 
being replaced by it. 
— Prof. Campbell Harvey, Duke University. Former President of the 
American Finance Association. 
 
Financial problems require very distinct machine learning solutions. Dr. 
López de Prado’s book is the first one to characterize what makes standard 
machine learning tools fail when applied to the field of finance, and the first 
one to provide practical solutions to unique challenges faced by asset 
managers. Everyone who wants to understand the future of finance should 
read this book. 
— Prof. Frank Fabozzi, EDHEC Business School. Editor of The Journal of 
Portfolio Management.


<!-- PAGE 25 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
THANKS FOR YOUR ATTENTION! 
 
 
 
25


<!-- PAGE 26 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
Bio 
Dr. Marcos López de Prado is a principal at AQR Capital Management, and its head of machine learning. Before AQR, 
he founded and led Guggenheim Partners’ Quantitative Investment Strategies (QIS) business, where he developed 
high-capacity machine learning strategies that consistently delivered superior risk-adjusted returns, receiving up to 
$13 billion in assets. 
Concurrently with the management of investments, between 2011 and 2018 Marcos was also a research fellow at 
Lawrence Berkeley National Laboratory (U.S. Department of Energy, Office of Science). He has published dozens of 
scientific articles on machine learning and supercomputing in the leading academic journals, and SSRN ranks him as 
one of the most-read authors in economics. Among several monographs, he is the author of the graduate textbook 
Advances in Financial Machine Learning (Wiley, 2018). 
Marcos earned a PhD in financial economics (2003), a second PhD in mathematical finance (2011) from Universidad 
Complutense de Madrid, and is a recipient of Spain's National Award for Academic Excellence (1999). He completed 
his post-doctoral research at Harvard University and Cornell University, where he teaches a financial machine 
learning course at the School of Engineering. Marcos has an Erdős #2 and an Einstein #4 according to the American 
Mathematical Society. 
For more information, please visit www.QuantResearch.org  
26


<!-- PAGE 27 -->

Electronic copy available at: https://ssrn.com/abstract=3257497 
Disclaimer 
• The views expressed in this document are the authors’ and do not necessarily 
reflect those of the organizations he is affiliated with. 
• No investment decision or particular course of action is recommended by this 
presentation. 
• All Rights Reserved. © 2018 by Marcos López de Prado 
27


<!-- PAGE 28 -->

本文献由“学霸图书馆-文献云下载”收集自网络，仅供学习交流使用。
学霸图书馆（www.xuebalib.com）是一个“整合众多图书馆数据库资源，
提供一站式文献检索和下载服务”的24
 
小时在线不限IP
 
图书馆。
图书馆致力于便利、促进学习与科研，提供最强文献下载服务。
图书馆导航：
图书馆首页   文献云下载   图书馆入口   外文数据库大全   疑难文献辅助工具
