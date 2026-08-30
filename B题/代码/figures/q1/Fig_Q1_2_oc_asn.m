%% Fig.Q1-2  问题一主情景 OC 与 ASN
clear; close all; clc;
here=fileparts(mfilename('fullpath')); dataDir=fullfile(here,'..','..','results','q1');
S=jsondecode(fileread(fullfile(dataDir,'summary.json'))); main=S.main_scenario;
T=readtable(fullfile(dataDir,'operating_characteristics.csv'),'VariableNamingRule','preserve');
T=T(abs(T.p1-main.p1)<1e-12 & abs(T.kappa-main.kappa)<1e-12,:); T=sortrows(T,'p');
p=T.p; fig=figure('Color','w','Name','Fig.Q1-2 OC ASN','NumberTitle','off');
tiledlayout(fig,1,2,'TileSpacing','compact','Padding','compact');
dark=[.12 .35 .58]; red=[.78 .18 .16]; gray=[.82 .88 .94]; ink=[.12 .12 .12];
ax1=nexttile; hold(ax1,'on'); set(ax1,'Color','w','XColor',ink,'YColor',ink,'Box','off','FontSize',10);
ha=plot(ax1,p,T.P_accept,'-o','Color',dark,'MarkerFaceColor',dark,'MarkerSize',3.5,'LineWidth',1.4);
hr=plot(ax1,p,T.P_reject,'--s','Color',red,'MarkerFaceColor',red,'MarkerSize',3.5,'LineWidth',1.2);
hp0=xline(ax1,main.p0,':','Color',ink,'LineWidth',1); hp1=xline(ax1,main.p1,':','Color',ink,'LineWidth',1);
h95=yline(ax1,.95,':','Color',[.35 .35 .35]); h10=yline(ax1,.10,':','Color',[.35 .35 .35]);
xlabel(ax1,'真实次品率 p','FontName',fontNameCN(),'Color',ink); ylabel(ax1,'概率','FontName',fontNameCN(),'Color',ink);
title(ax1,'(a) 操作特性曲线（OC）','FontName',fontNameCN(),'FontWeight','normal','Color',ink);
legend(ax1,[ha hr hp0 hp1 h95 h10],{'P_{accept}(p)','P_{reject}(p)','p_0=0.10','p_1=0.13','1−α=0.95','β=0.10'}, ...
    'Location','southwest','FontName',fontNameCN(),'Box','off','TextColor',ink,'Color','w','Interpreter','tex');
ylim(ax1,[0 1]); grid(ax1,'on'); ax1.GridAlpha=.16;
text(ax1,main.p0+.002,.18,sprintf('P_{p_0}(R)=%.6f',S.main_endpoint_checks.at_p0.P_reject),'FontName','Times New Roman','FontSize',8,'Color',ink);
text(ax1,main.p1+.002,.78,sprintf('P_{p_1}(A)=%.6f',S.main_endpoint_checks.at_p1.P_accept),'FontName','Times New Roman','FontSize',8,'Color',ink);

ax2=nexttile; hold(ax2,'on'); set(ax2,'Color','w','XColor',ink,'YColor',ink,'Box','off','FontSize',10);
yl=max(T.ASN)*1.08; patch(ax2,[main.p0 main.p1 main.p1 main.p0],[0 0 yl yl],gray,'EdgeColor','none','FaceAlpha',.55);
plot(ax2,p,T.ASN,'-o','Color',dark,'MarkerFaceColor',dark,'MarkerSize',3.5,'LineWidth',1.4);
xline(ax2,main.p0,':','Color',ink); xline(ax2,main.p1,':','Color',ink);
plot(ax2,main.p_worst_grid,main.J_ASN_grid,'p','Color',[.78 .18 .16],'MarkerFaceColor',[.78 .18 .16],'MarkerSize',9);
xlabel(ax2,'真实次品率 p','FontName',fontNameCN(),'Color',ink); ylabel(ax2,'ASN（件）','FontName',fontNameCN(),'Color',ink);
title(ax2,'(b) 平均抽样量（ASN）','FontName',fontNameCN(),'FontWeight','normal','Color',ink);
legend(ax2,{'无差异区 [p_0,p_1]','ASN(p)','灰区最坏点'},'Location','best','FontName',fontNameCN(),'Box','off','TextColor',ink,'Color','w');
grid(ax2,'on'); ax2.GridAlpha=.16;
text(ax2,main.p_worst_grid,main.J_ASN_grid,sprintf('  p=%.6f, J=%.3f',main.p_worst_grid,main.J_ASN_grid), ...
    'FontName','Times New Roman','FontSize',8,'Color',ink,'VerticalAlignment','bottom');
sgtitle(fig,'问题一主情景的 OC 与 ASN', ...
    'FontName',fontNameCN(),'FontWeight','normal','Color',ink);

function name=fontNameCN()
fonts=listfonts; candidates={'Noto Serif CJK SC','Source Han Serif SC','SimSun','Songti SC','Microsoft YaHei'};
name='DejaVu Serif'; for i=1:numel(candidates), if any(strcmpi(fonts,candidates{i})), name=candidates{i}; return; end, end
end
