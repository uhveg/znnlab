clear;close all;clc;
tau = 0.01;gamma = 0.4/tau;h = tau*gamma;
A = @(t) [sin(t),cos(t);-cos(t),sin(t)];
dA = @(t) [cos(t),-sin(t);sin(t),cos(t)];

% X0 = 2*A(0)'/(trace(A(0)*A(0)'));
X0 = eye(2);
X1 = X0 - tau*X0*dA(0)*X0 - h*X0*(A(0)*X0-eye(2));
X2 = X1 - tau*X1*dA(1*tau)*X1 - h*X1*(A(1*tau)*X1-eye(2));
X3 = X2 - tau*X2*dA(2*tau)*X2 - h*X2*(A(2*tau)*X2-eye(2));
X4 = X3 - tau*X3*dA(3*tau)*X3 - h*X3*(A(3*tau)*X3-eye(2));

output = sim('One_Step_DTZNN.slx', 'StopTime', '10', 'Solver', 'ode4', 'FixedStep', num2str(tau));
output2 = sim('Three_Step_DTZNN.slx',   'StopTime', '10', 'Solver', 'ode4', 'FixedStep', num2str(tau));
output3 = sim('Five_Step_DTZNN.slx', 'StopTime', '10', 'Solver', 'ode4', 'FixedStep', num2str(tau));

figure('OuterPosition',[360,90,1200,900]);
for i=1:4
    subplot(2,2,i);hold on; grid minor;
    titleHandle = title(sprintf('$x_{%d,%d}$',ceil(i/2),2-mod(i,2)), 'Interpreter', 'latex');
    set(titleHandle, 'Units', 'normalized', 'Position', [0.5, 0.85, 0]);
    ylim([-2,2]);
    plot(output.invA.Time, output.invA.Data(:,i), 'r');
    plot(output.X.Time, output.X.Data(:,i), 'b--');
end
show(output);
return;


%% PLOT COMPARATIVE
figure;hold on;grid minor;
xlabel('tiempo(s)', 'Interpreter', 'latex');
ylabel('$\| A(t)X(t) - I \|_F$', 'Interpreter', 'latex');
title('Comparativa modelos en tiempo discreto');
plot(output.frobNorm.Time, output.frobNorm.Data);
plot(output2.frobNorm.Time, output2.frobNorm.Data);
plot(output3.frobNorm.Time, output3.frobNorm.Data);
xlim([0,1])
set(gca, 'YLimSpec', 'Padded');
legend('One-Step DTZNN', 'Three-Step DTZNN', 'Five-Step DTZNN')
axes('position',[.6 .21 .28 .25]);box on;grid minor;hold on;
set(gca, 'YScale', 'log');
set(gca, 'YLimSpec', 'Padded');
yticks([2.20e-8, 2.35e-6, 1.76e-4]);
ytickformat('%.2e');
indexOfInterest = (output.frobNorm.Time > 8);
plot(output.frobNorm.Time(indexOfInterest), output.frobNorm.Data(indexOfInterest));
plot(output2.frobNorm.Time(indexOfInterest), output2.frobNorm.Data(indexOfInterest));
plot(output3.frobNorm.Time(indexOfInterest), output3.frobNorm.Data(indexOfInterest));

function show(out)
    figure;hold on;grid minor;
    xlabel('tiempo(s)', 'Interpreter', 'latex');
    title('$\| A(t)X(t) - I \|_F$', 'Interpreter', 'latex');
    plot(out.frobNorm.Time, out.frobNorm.Data);
    set(gca, 'YLimSpec', 'Padded');
    xlim([0,1])
end