%% Fig.Q1-3  p_1-kappa 双重敏感性
clear; close all; clc;
here=fileparts(mfilename('fullpath')); dataDir=fullfile(here,'..','..','results','q1');
T=readtable(fullfile(dataDir,'sequential_plans.csv'),'VariableNamingRule','preserve');
p1v=sort(unique(T.p1)); kv=sort(unique(T.kappa));
J=nan(numel(p1v),numel(kv)); saving=J; nmax=J;
for i=1:numel(p1v)
    for j=1:numel(kv)
        row=T(abs(T.p1-p1v(i))<1e-12 & abs(T.kappa-kv(j))<1e-12,:);
        if height(row)==1, J(i,j)=row.J_ASN_grid; saving(i,j)=100*row.ASN_saving_vs_fixed; nmax(i,j)=row.N_max; end
    end
end
fig=figure('Color','w','Name','Fig.Q1-3 敏感性','NumberTitle','off');
tiledlayout(fig,1,2,'TileSpacing','compact','Padding','compact'); ink=[.12 .12 .12];
ax1=nexttile; imagesc(ax1,J); set(ax1,'YDir','normal','Color','w','XColor',ink,'YColor',ink,'Box','off');
colormap(ax1,parula(256)); colorbar(ax1); set(ax1,'XTick',1:numel(kv),'XTickLabel',compose('%.2g',kv), ...
    'YTick',1:numel(p1v),'YTickLabel',compose('%.2f',p1v),'FontName',fontNameCN(),'FontSize',10);
xlabel(ax1,'截尾倍率 \kappa','FontName',fontNameCN(),'Color',ink,'Interpreter','tex'); ylabel(ax1,'LTPD 情景 p_1','FontName',fontNameCN(),'Color',ink,'Interpreter','tex');
title(ax1,'(a) 灰区最坏 ASN','FontName',fontNameCN(),'FontWeight','normal','Color',ink);
annotate(ax1,J,'%.1f');
ax2=nexttile; imagesc(ax2,saving); set(ax2,'YDir','normal','Color','w','XColor',ink,'YColor',ink,'Box','off');
colormap(ax2,parula(256)); colorbar(ax2); set(ax2,'XTick',1:numel(kv),'XTickLabel',compose('%.2g',kv), ...
    'YTick',1:numel(p1v),'YTickLabel',compose('%.2f',p1v),'FontName',fontNameCN(),'FontSize',10);
xlabel(ax2,'截尾倍率 \kappa','FontName',fontNameCN(),'Color',ink,'Interpreter','tex'); ylabel(ax2,'LTPD 情景 p_1','FontName',fontNameCN(),'Color',ink,'Interpreter','tex');
title(ax2,'(b) 相对固定抽样节省率（%）','FontName',fontNameCN(),'FontWeight','normal','Color',ink);
annotate(ax2,saving,'%.2f');
sgtitle(fig,'问题一质量分辨率与截尾倍率的抽样效率敏感性（局部校准网格）', ...
    'FontName',fontNameCN(),'FontWeight','normal','Color',ink);

function annotate(ax,A,fmt)
mx=max(A(:),[],'omitnan'); mn=min(A(:),[],'omitnan');
for i=1:size(A,1), for j=1:size(A,2)
    if isfinite(A(i,j))
        if A(i,j)>.55*mx, c=[1 1 1]; else, c=[.1 .1 .1]; end
        text(ax,j,i,sprintf(fmt,A(i,j)),'HorizontalAlignment','center','FontName','Times New Roman','FontSize',8,'Color',c,'FontWeight','bold');
    end
end, end
end

function name=fontNameCN()
fonts=listfonts; candidates={'Noto Serif CJK SC','Source Han Serif SC','SimSun','Songti SC','Microsoft YaHei'};
name='DejaVu Serif'; for i=1:numel(candidates), if any(strcmpi(fonts,candidates{i})), name=candidates{i}; return; end, end
end
