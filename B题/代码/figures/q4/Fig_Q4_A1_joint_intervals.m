%% Fig.Q4-A1  演示固定样本下质量参数的联合置信区间（附录）
clear; close all; clc;
here=fileparts(mfilename('fullpath')); dataDir=fullfile(here,'..','..','results','q4');
I=readtable(fullfile(dataDir,'simultaneous_intervals.csv'),'VariableNamingRule','preserve');
E=jsondecode(fileread(fullfile(dataDir,'evidence_used.json'))); ink=[.12 .12 .12];
% 附录选取 Q2 情形1 与 Q3，避免重复绘制六个完全同构的 Q2 情形。
I=I((strcmp(string(I.domain),'q2') & I.('case')==1) | strcmp(string(I.domain),'q3'),:);
names={}; est=[]; lo90=[]; hi90=[]; lo95=[]; hi95=[];
for i=1:height(I)
    key=char(string(I.parameter(i))); d=char(string(I.domain(i)));
    if strcmp(d,'q2'), rec=E.q2.case_1.(key); prefix='Q2-'; else, rec=E.q3.(key); prefix='Q3-'; end
    if ~any(strcmp(names,[prefix key])), names{end+1}=[prefix key]; est(end+1)=rec.K/rec.N; lo90(end+1)=nan; hi90(end+1)=nan; lo95(end+1)=nan; hi95(end+1)=nan; end %#ok<AGROW>
    k=find(strcmp(names,[prefix key]),1); if I.coverage(i)==90, lo90(k)=I.lower(i); hi90(k)=I.upper(i); else, lo95(k)=I.lower(i); hi95(k)=I.upper(i); end
end
y=1:numel(names); fig=figure('Color','w','Name','Fig.Q4-A1 联合区间','NumberTitle','off'); ax=axes(fig,'Color','w','XColor',ink,'YColor',ink); hold(ax,'on');
for k=1:numel(y)
    if isfinite(lo95(k)), errorbar(ax,est(k),y(k),est(k)-lo95(k),hi95(k)-est(k),'horizontal','s','Color',[.85 .47 .18],'LineWidth',1.0,'CapSize',5); end
    if isfinite(lo90(k)), errorbar(ax,est(k),y(k),est(k)-lo90(k),hi90(k)-est(k),'horizontal','o','Color',[.12 .35 .58],'LineWidth',1.0,'CapSize',5); end
end
plot(ax,est,y,'k.','MarkerSize',13); set(ax,'YTick',y,'YTickLabel',names,'YDir','reverse','FontName',fontNameCN(),'FontSize',9,'Box','off');
xlabel(ax,'次品率 p','FontName',fontNameCN(),'Color',ink); ylabel(ax,'参数（情形1或Q3）','FontName',fontNameCN(),'Color',ink);
title(ax,'演示固定样本下质量参数的联合置信区间','FontName',fontNameCN(),'FontWeight','normal','Color',ink);
plot(ax,nan,nan,'-o','Color',[.12 .35 .58]); plot(ax,nan,nan,'-s','Color',[.85 .47 .18]); plot(ax,nan,nan,'k.','MarkerSize',13);
legend(ax,{'90% 联合区间','95% 联合区间','点估计 K/N'},'Location','best','FontName',fontNameCN(),'Box','off','TextColor',ink,'Color','w');
xlim(ax,[0 max(0.35,max(hi95,[],'omitnan')*1.08)]); grid(ax,'on'); ax.GridAlpha=.16;
annotation(fig,'textbox',[.15 .005 .7 .035],'String','区间采用 fixed-n Clopper–Pearson 方法，并按 Bonferroni 分配联合覆盖率；仅作稳健审计附录。','EdgeColor','none','HorizontalAlignment','center','FontName',fontNameCN(),'FontSize',9,'Color',ink);

function name=fontNameCN()
fonts=listfonts; candidates={'Noto Serif CJK SC','Source Han Serif SC','SimSun','Songti SC','Microsoft YaHei'}; name='DejaVu Serif';
for i=1:numel(candidates), if any(strcmpi(fonts,candidates{i})), name=candidates{i}; return; end, end
end
