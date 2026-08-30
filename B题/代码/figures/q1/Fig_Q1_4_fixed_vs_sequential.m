%% Fig.Q1-4  固定抽样与序贯抽样的样本负担比较
clear; close all; clc;
here=fileparts(mfilename('fullpath')); dataDir=fullfile(here,'..','..','results','q1');
F=readtable(fullfile(dataDir,'fixed_binomial_baselines.csv'),'VariableNamingRule','preserve');
P=readtable(fullfile(dataDir,'sequential_plans.csv'),'VariableNamingRule','preserve');
% 取最小声明截尾倍率，作为每个 p_1 的主序贯比较方案。
k0=min(P.kappa); P=P(abs(P.kappa-k0)<1e-12,:); P=sortrows(P,'p1'); F=sortrows(F,'p1');
[~,ia,ib]=intersect(F.p1,P.p1,'stable'); F=F(ia,:); P=P(ib,:);
fig=figure('Color','w','Name','Fig.Q1-4 固定与序贯','NumberTitle','off');
tiledlayout(fig,1,2,'TileSpacing','compact','Padding','compact'); ink=[.12 .12 .12];
ax1=nexttile; hold(ax1,'on');
bar(ax1,[F.n_fixed P.J_ASN_grid],'grouped');
set(ax1,'Color','w','XColor',ink,'YColor',ink,'Box','off','FontName',fontNameCN(),'FontSize',10, ...
    'XTick',1:height(F),'XTickLabel',compose('%.2f',F.p1));
xlabel(ax1,'LTPD 情景 p_1','FontName',fontNameCN(),'Color',ink); ylabel(ax1,'样本量（件）','FontName',fontNameCN(),'Color',ink);
title(ax1,'(a) 固定样本量与序贯灰区最坏 ASN','FontName',fontNameCN(),'FontWeight','normal','Color',ink);
legend(ax1,{'固定抽样 n_F','序贯方案 J_{ASN}'},'Location','northwest','FontName',fontNameCN(),'Box','off','TextColor',ink,'Color','w');
grid(ax1,'on'); ax1.GridAlpha=.16;
ax2=nexttile; hold(ax2,'on');
plot(ax2,F.p1,F.n_fixed,'-o','Color',[.45 .45 .45],'MarkerFaceColor',[.45 .45 .45],'LineWidth',1.3);
plot(ax2,P.p1,P.N_max,'-s','Color',[.12 .35 .58],'MarkerFaceColor',[.12 .35 .58],'LineWidth',1.3);
set(ax2,'Color','w','XColor',ink,'YColor',ink,'Box','off','FontName',fontNameCN(),'FontSize',10);
xlabel(ax2,'LTPD 情景 p_1','FontName',fontNameCN(),'Color',ink); ylabel(ax2,'最大抽检数（件）','FontName',fontNameCN(),'Color',ink);
title(ax2,sprintf('(b) 最大抽检数（\\kappa=%.2g）',k0),'FontName',fontNameCN(),'FontWeight','normal','Color',ink);
legend(ax2,{'固定抽样 n_F','序贯方案 N_{max}'},'Location','northwest','FontName',fontNameCN(),'Box','off','TextColor',ink,'Color','w');
grid(ax2,'on'); ax2.GridAlpha=.16;
sgtitle(fig,'相同双风险约束下固定抽样与序贯抽样的样本负担比较', ...
    'FontName',fontNameCN(),'FontWeight','normal','Color',ink);

function name=fontNameCN()
fonts=listfonts; candidates={'Noto Serif CJK SC','Source Han Serif SC','SimSun','Songti SC','Microsoft YaHei'};
name='DejaVu Serif'; for i=1:numel(candidates), if any(strcmpi(fonts,candidates{i})), name=candidates{i}; return; end, end
end
