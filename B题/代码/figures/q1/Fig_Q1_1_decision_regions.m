%% Fig.Q1-1  问题一主情景下序贯验收决策边界
clear; close all; clc;
here = fileparts(mfilename('fullpath')); dataDir = fullfile(here,'..','..','results','q1');
S = jsondecode(fileread(fullfile(dataDir,'summary.json')));
main = S.main_scenario;
D = readtable(fullfile(dataDir,'decision_boundaries.csv'),'VariableNamingRule','preserve');
mask = abs(D.p1-main.p1)<1e-12 & abs(D.kappa-main.kappa)<1e-12;
D = D(mask,:); D = sortrows(D,'n');
N = main.N_max; cN = main.c_N; n = D.n(:)';
a = D.k_accept_max(:)'; r = D.k_reject_min(:)';
% 矩阵颜色只表示 A/C/R；k>n 的不可达区域设为 NaN。
region = nan(N+1,N);
for j = 1:N
    k = 0:N;
    if j < N
        aa = a(j); rr = r(j);
        region(k<=j & k<=aa,j) = 1;
        region(k<=j & k>aa & k<rr,j) = 2;
        region(k<=j & k>=rr,j) = 3;
    else
        region(k<=j & k<=cN,j) = 1;
        region(k<=j & k>cN,j) = 3;
    end
end

fig = figure('Color','w','Name','Fig.Q1-1 决策区域','NumberTitle','off');
ax = axes(fig,'Color','w','XColor',[.12 .12 .12],'YColor',[.12 .12 .12]); hold(ax,'on');
imagesc(ax,1:N,0:N,region); set(ax,'YDir','normal');
colormap(ax,[0.25 0.55 0.75; 0.92 0.92 0.92; 0.85 0.38 0.32]);
set(ax,'FontName',fontNameCN(),'FontSize',10,'Box','off','LineWidth',.8);
validA = isfinite(a); validR = isfinite(r);
stairs(ax,n(validA),a(validA),'Color',[.05 .25 .45],'LineWidth',1.4);
stairs(ax,n(validR),r(validR),'Color',[.55 .12 .10],'LineWidth',1.4);
xline(ax,N,'--','Color',[.12 .12 .12],'LineWidth',1.1);
pA=patch(ax,nan,nan,[.25 .55 .75],'EdgeColor','none');
pC=patch(ax,nan,nan,[.92 .92 .92],'EdgeColor','none');
pR=patch(ax,nan,nan,[.85 .38 .32],'EdgeColor','none');
lA=plot(ax,nan,nan,'-','Color',[.05 .25 .45],'LineWidth',1.4);
lR=plot(ax,nan,nan,'-','Color',[.55 .12 .10],'LineWidth',1.4);
lN=plot(ax,nan,nan,'--','Color',[.12 .12 .12],'LineWidth',1.1);
xlabel(ax,'累计抽检数 n','FontName',fontNameCN(),'Color',[.12 .12 .12]);
ylabel(ax,'累计次品数 k','FontName',fontNameCN(),'Color',[.12 .12 .12]);
title(ax,sprintf('问题一主情景序贯验收决策边界（p_0=%.2f, p_1=%.2f, \\kappa=%.2g）', ...
    S.main_scenario.p0,S.main_scenario.p1,S.main_scenario.kappa), ...
    'FontName',fontNameCN(),'FontWeight','normal','Color',[.12 .12 .12]);
legend(ax,[pA pC pR lA lR lN],{'接收区域','继续抽样区域','拒收区域','接收边界 a_n','拒收边界 r_n','N_{max} 截尾线'}, ...
    'Location','northoutside','Orientation','horizontal','FontName',fontNameCN(), ...
    'TextColor',[.12 .12 .12],'Color','w','Box','off');
xlim(ax,[1 N]); ylim(ax,[0 min(N, max(20,ceil(max(r(isfinite(r))))+5))]);
text(ax,N-5,min(ylim(ax))*0+max(ylim(ax))*.92,sprintf('N_{max}=%d, c_N=%d',N,cN), ...
    'HorizontalAlignment','right','FontName','Times New Roman','FontSize',9,'Color',[.12 .12 .12]);

function name = fontNameCN()
fonts=listfonts; candidates={'Noto Serif CJK SC','Source Han Serif SC','SimSun','Songti SC','Microsoft YaHei'};
name='DejaVu Serif'; for i=1:numel(candidates), if any(strcmpi(fonts,candidates{i})), name=candidates{i}; return; end, end
end
